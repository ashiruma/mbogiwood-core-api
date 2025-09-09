import json
import logging
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from films.models import Film
from .models import Order, PaymentTransaction, Payout, PayoutRequest
from .serializers import (
    OrderSerializer,
    PaymentTransactionSerializer,
    PayoutSerializer,
    PayoutRequestSerializer,
)
from .utils import stk_push, b2c_payment

logger = logging.getLogger(__name__)
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)


# -------------------------
# Healthcheck
# -------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def ping(request):
    """A simple healthcheck endpoint to confirm the app is running."""
    return Response({"status": "ok", "app": "payments"})


# -------------------------
# Stripe Checkout Session
# -------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_stripe_checkout_session(request, film_id):
    """Creates a Stripe Checkout session for purchasing a film."""
    film = get_object_or_404(Film, id=film_id, status=Film.PAID)

    order = Order.objects.create(
        user=request.user,
        film=film,
        payment_method=Order.PaymentMethod.STRIPE,
        amount_cents=int(film.price * 100),
        currency=getattr(film, "currency", "USD"),
        status=Order.Status.PENDING,
    )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": order.currency.lower(),
                    "product_data": {"name": film.title},
                    "unit_amount": order.amount_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(
                reverse("payments:payment-success")
            ) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("payments:payment-cancel")),
            metadata={"order_id": str(order.id)},
        )
    except Exception as e:
        logger.exception("Stripe session creation failed")
        order.status = Order.Status.FAILED
        order.save(update_fields=["status"])
        return Response({"error": str(e)}, status=500)

    order.payment_id = session.id
    order.save(update_fields=["payment_id"])

    return Response({"id": session.id, "checkout_url": session.url})


def payment_success(request):
    """Renders the success page after a Stripe payment."""
    return render(request, "payments/success.html", {"session_id": request.GET.get("session_id")})


def payment_cancel(request):
    """Renders the cancellation page after a Stripe payment."""
    return render(request, "payments/cancel.html")


# -------------------------
# M-Pesa STK Push
# -------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_mpesa_payment(request):
    """Initiates an M-Pesa STK Push payment for a film."""
    data = request.data
    film_id = data.get("film_id")
    phone = data.get("phone")

    if not film_id or not phone:
        return Response({"error": "film_id and phone are required"}, status=400)

    film = get_object_or_404(Film, id=film_id, status=Film.PAID)

    order = Order.objects.create(
        user=request.user,
        film=film,
        payment_method=Order.PaymentMethod.MPESA,
        amount_cents=int(film.price * 100),
        currency="KES",
        status=Order.Status.PENDING,
        phone_number=phone,
    )

    try:
        res = stk_push(
            phone_number=phone,
            amount=order.amount_cents // 100,  # Amount in KES
            account_reference=f"Film-{film.id}",
            transaction_desc=f"Payment for {film.title}"
        )
    except Exception as e:
        logger.exception("STK push failed")
        order.status = Order.Status.FAILED
        order.save(update_fields=["status"])
        return Response({"error": str(e)}, status=500)

    checkout_id = res.get("CheckoutRequestID")
    if checkout_id:
        order.payment_id = checkout_id
        order.save(update_fields=["payment_id"])

        PaymentTransaction.objects.create(
            checkout_request_id=checkout_id,
            merchant_request_id=res.get("MerchantRequestID"),
            amount_cents=order.amount_cents,
            phone_number=phone,
            status="PENDING",
        )

    return Response(res)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def mpesa_stk_callback(request):
    """
    The callback URL that Safaricom hits after an STK Push completes.
    This view processes the result and updates the order status.
    """
    payload = request.data if hasattr(request, "data") else json.loads(request.body.decode("utf-8"))
    logger.info("M-Pesa STK Callback payload: %s", json.dumps(payload))

    stk = payload.get("Body", {}).get("stkCallback", {}) if isinstance(payload, dict) else {}
    checkout_request_id = stk.get("CheckoutRequestID")
    result_code = stk.get("ResultCode")
    result_desc = stk.get("ResultDesc")
    
    # Acknowledge receipt of the callback immediately
    daraja_ack = {"ResultCode": 0, "ResultDesc": "Accepted"}

    if not checkout_request_id:
        return JsonResponse(daraja_ack)

    try:
        payment_txn = PaymentTransaction.objects.get(checkout_request_id=checkout_request_id)
        
        # Parse metadata for receipt, amount, etc.
        callback_items = stk.get("CallbackMetadata", {}).get("Item", []) or []
        for item in callback_items:
            name, val = item.get("Name"), item.get("Value")
            if name == "MpesaReceiptNumber":
                payment_txn.mpesa_receipt = val
            elif name == "Amount":
                payment_txn.amount_cents = int(float(val) * 100)
            elif name == "PhoneNumber":
                payment_txn.phone_number = val

        # Update transaction status
        payment_txn.result_code = result_code
        payment_txn.result_desc = result_desc
        payment_txn.status = "SUCCESS" if result_code == 0 else "FAILED"
        payment_txn.completed_at = timezone.now()
        payment_txn.save()

        # Update the master order
        order = Order.objects.filter(payment_id=checkout_request_id).first()
        if order:
            if result_code == 0:
                order.transaction_id = payment_txn.mpesa_receipt or order.transaction_id
                order.activate_access()  # This method should set status to SUCCESS and save
            else:
                order.status = Order.Status.FAILED
                order.save(update_fields=["status"])

    except PaymentTransaction.DoesNotExist:
        logger.error(f"PaymentTransaction with CheckoutRequestID {checkout_request_id} not found.")
    except Exception:
        logger.exception("Error processing M-Pesa STK callback")

    return JsonResponse(daraja_ack)


# -------------------------
# Payouts (Filmmaker -> Bank/M-Pesa)
# -------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated]) # Or IsAdminUser
def create_payout(request):
    """
    Initiates a B2C M-Pesa Payout to a filmmaker.
    Requires amount_cents and phone_number in the request body.
    """
    amount_cents = int(request.data.get("amount_cents", 0))
    phone_number = request.data.get("phone_number")

    if amount_cents <= 0 or not phone_number:
        return Response({"error": "amount_cents and phone_number are required"}, status=400)

    payout = Payout.objects.create(
        filmmaker=request.user,  # Assuming the admin initiates for a user
        amount_cents=amount_cents,
        status=Payout.Status.PENDING,
    )

    try:
        res = b2c_payment(phone_number=phone_number, amount=amount_cents // 100)
        
        # ✅ FIX: Save the unique OriginatorConversationID to track the callback
        payout.originator_conversation_id = res.get("OriginatorConversationID")
        payout.transaction_id = res.get("ConversationID") # Keep for reference
        payout.save()

    except Exception as e:
        logger.exception("B2C payout failed")
        payout.status = Payout.Status.FAILED
        payout.save(update_fields=["status"])
        return Response({"error": str(e)}, status=500)

    return Response({"ok": True, "payout_id": payout.id, "status": payout.status})


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def mpesa_b2c_result(request):
    """Callback for the result of a B2C Payout transaction."""
    payload = request.data if hasattr(request, "data") else json.loads(request.body.decode("utf-8"))
    logger.info("M-Pesa B2C Result payload: %s", json.dumps(payload))

    result = payload.get("Result", {})
    
    # ✅ FIX: Get the unique ID from the callback payload to find the exact payout record
    # Note: Safaricom's key for this can vary. Check your callback data. It's often in ReferenceData or OriginatorConversationID.
    # We will assume it's passed back as OriginatorConversationID in the top-level result for this example.
    originator_id = result.get("OriginatorConversationID")

    try:
        payout = Payout.objects.get(originator_conversation_id=originator_id)
        
        payout.mpesa_transaction_id = result.get("TransactionID")
        payout.status = Payout.Status.SUCCESS if result.get("ResultCode") == 0 else Payout.Status.FAILED
        payout.completed_at = timezone.now()
        payout.save()
        logger.info(f"Updated payout {payout.id} to status {payout.status}")

    except Payout.DoesNotExist:
        logger.error(f"Could not find a Payout matching OriginatorConversationID: {originator_id}")
    except Exception:
        logger.exception(f"Error processing B2C result for OriginatorID {originator_id}")

    return JsonResponse({"ResultCode": 0, "ResultDesc": "B2C Result processed"})


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def mpesa_b2c_timeout(request):
    """Callback for a B2C Payout that has timed out."""
    payload = request.data if hasattr(request, "data") else json.loads(request.body.decode("utf-8"))
    logger.warning("M-Pesa B2C Timeout payload: %s", json.dumps(payload))
    # You might want to find the related payout and mark it as timed out or failed.
    return JsonResponse({"ResultCode": 0, "ResultDesc": "B2C Timeout received"})


# -------------------------
# Payout Requests (Filmmaker asks for money)
# -------------------------
class PayoutRequestCreateView(generics.CreateAPIView):
    """Allows an authenticated filmmaker to create a request for a payout."""
    queryset = PayoutRequest.objects.all()
    serializer_class = PayoutRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(filmmaker=self.request.user)


class PayoutRequestListView(generics.ListAPIView):
    """Lists all payout requests for the currently authenticated filmmaker."""
    serializer_class = PayoutRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PayoutRequest.objects.filter(filmmaker=self.request.user)


# -------------------------
# Check Film Access API
# -------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def film_access_api(request, film_id):
    """Checks if the logged-in user has active access to a given film."""
    film = get_object_or_404(Film, id=film_id)

    order = Order.objects.filter(
        user=request.user, film=film, status=Order.Status.SUCCESS
    ).first()

    if order and order.has_access():
        return Response({
            "access": True,
            "expires_at": order.access_expires_at.isoformat() if order.access_expires_at else None,
            "stream_url": request.build_absolute_uri(
                reverse("films:film-stream-api", args=[film.id])
            ),
        })

    return Response({"access": False})