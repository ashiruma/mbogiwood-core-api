# payments/views.py
import json
import logging
from datetime import timedelta

import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from films.models import Film
from .models import Order, PaymentTransaction, Payout
from .utils import stk_push  # your helper for Daraja / STK push

logger = logging.getLogger(__name__)
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)


# -------------------------
# Basic ping for healthcheck
# -------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def ping(request):
    return Response({"status": "ok", "app": "payments"})


# -------------------------
# Stripe Checkout (class-based)
# -------------------------
class CreateStripeCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, film_id):
        """
        Create a Stripe Checkout session and an Order in PENDING state.
        Note: This uses film.price_cents (expected integer, cents).
        """
        film = get_object_or_404(Film, id=film_id, status=Film.PAID)

        # Create Order (amount_cents stored)
        order = Order.objects.create(
            user=request.user,
            film=film,
            payment_method=Order.PaymentMethod.STRIPE,
            amount_cents=getattr(film, "price_cents", 0) or 0,
            currency=getattr(film, "currency", "KES"),
            status=Order.Status.PENDING,
        )

        # Build Stripe session line item (expects amount in cents)
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd" if getattr(settings, "STRIPE_USE_USD", False) else "kes",
                        "product_data": {"name": film.title},
                        "unit_amount": int(order.amount_cents),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=request.build_absolute_uri(f"/payments/success/?session_id={{CHECKOUT_SESSION_ID}}"),
                cancel_url=request.build_absolute_uri("/payments/cancel/"),
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


# -------------------------
# Stripe success/cancel pages (simple renders)
# -------------------------
def payment_success(request):
    # You can keep a template or return a simple page
    session_id = request.GET.get("session_id")
    return render(request, "payments/success.html", {"session_id": session_id})


def payment_cancel(request):
    return render(request, "payments/cancel.html")


# -------------------------
# Watch film (template)
# -------------------------
def watch_film(request, film_id):
    """
    Render watch page: allow if PROMO or user has a successful order with access.
    """
    film = get_object_or_404(Film, id=film_id)
    unlocked = False

    if film.status == Film.PROMO:
        unlocked = True
    elif request.user.is_authenticated:
        # check for successful order with non-expired access
        unlocked = Order.objects.filter(
            user=request.user,
            film=film,
            status=Order.Status.SUCCESS,
            access_expires_at__gt=timezone.now()
        ).exists()

    return render(request, "films/watch.html", {"film": film, "unlocked": unlocked})


# -------------------------
# M-Pesa STK Push (initiate)
# -------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_mpesa_payment(request):
    """
    Initiates an M-Pesa STK push for a film.
    Expected payload (JSON):
    {
      "film_id": <id>,
      "phone": "+2547XXXXXXXX"
    }
    Returns the raw Daraja response (or error).
    """
    data = request.data or {}
    film_id = data.get("film_id")
    phone = data.get("phone")

    if not film_id or not phone:
        return Response({"error": "film_id and phone are required"}, status=400)

    film = get_object_or_404(Film, id=film_id, status=Film.PAID)

    # Create Order (amount_cents)
    order = Order.objects.create(
        user=request.user,
        film=film,
        payment_method=Order.PaymentMethod.MPESA,
        amount_cents=getattr(film, "price_cents", 0) or 0,
        currency=getattr(film, "currency", "KES"),
        status=Order.Status.PENDING,
        phone_number=phone,
    )

    # Call the util to send STK push. Expect util to return a dict with 'CheckoutRequestID' or error.
    try:
        # stk_push here should return the response dict from Daraja
        res = stk_push(phone=phone, amount_cents=order.amount_cents, order_id=order.id)
    except Exception as e:
        logger.exception("STK push failed")
        order.status = Order.Status.FAILED
        order.save(update_fields=["status"])
        return Response({"error": str(e)}, status=500)

    # Example expected success response contains CheckoutRequestID
    checkout_id = res.get("CheckoutRequestID") or res.get("CheckoutRequestID")
    if checkout_id:
        order.payment_id = checkout_id
        order.save(update_fields=["payment_id"])

        # Log payment transaction (map fields to your PaymentTransaction model)
        PaymentTransaction.objects.create(
            checkout_request_id=checkout_id,
            merchant_request_id=res.get("MerchantRequestID") or res.get("MerchantRequestID"),
            amount_cents=order.amount_cents,
            phone_number=phone,
            status="PENDING",
        )

    return Response(res)


# -------------------------
# M-Pesa Callback
# -------------------------
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def mpesa_callback(request):
    """
    Daraja will POST JSON callback here.
    The structure is the standard stkCallback under Body.
    We:
      - update PaymentTransaction
      - find Order by checkout_request_id and activate
    """
    payload = request.data if hasattr(request, "data") else json.loads(request.body.decode("utf-8"))

    logger.info("M-Pesa Callback payload: %s", json.dumps(payload))

    # Safely traverse structure
    stk = payload.get("Body", {}).get("stkCallback", {}) if isinstance(payload, dict) else {}
    checkout_request_id = stk.get("CheckoutRequestID")
    result_code = stk.get("ResultCode")
    result_desc = stk.get("ResultDesc")

    # find transaction by checkout_request_id
    payment_txn = None
    if checkout_request_id:
        payment_txn = PaymentTransaction.objects.filter(checkout_request_id=checkout_request_id).first()

    # default response for Daraja
    daraja_ack = {"ResultCode": 0, "ResultDesc": "Accepted"}

    # If no checkout id, just return ack
    if not checkout_request_id:
        logger.warning("mpesa_callback: no CheckoutRequestID found")
        return JsonResponse(daraja_ack)

    # Parse metadata items if present
    callback_items = stk.get("CallbackMetadata", {}).get("Item", []) or []

    receipt = None
    amount = None
    phone = None

    for item in callback_items:
        name = item.get("Name")
        val = item.get("Value")
        if name == "MpesaReceiptNumber":
            receipt = val
        elif name == "Amount":
            amount = val
        elif name == "PhoneNumber":
            phone = val

    try:
        # Update transaction log
        if payment_txn:
            payment_txn.result_desc = result_desc
            payment_txn.result_code = result_code
            if receipt:
                payment_txn.mpesa_receipt = receipt
            if amount:
                # convert to cents (Daraja returns amount in KES)
                payment_txn.amount_cents = int(float(amount) * 100)
            if phone:
                payment_txn.phone_number = phone
            payment_txn.status = "SUCCESS" if result_code == 0 else "FAILED"
            payment_txn.completed_at = timezone.now()
            payment_txn.save()

        # find the order that referenced this checkout_request_id
        order = Order.objects.filter(payment_id=checkout_request_id).first()
        if not order and phone:
            # fallback: find by phone pending orders
            order = Order.objects.filter(phone_number=phone, status=Order.Status.PENDING).order_by("-created_at").first()

        if not order:
            logger.warning("mpesa_callback: no order found for checkout id %s", checkout_request_id)
        else:
            if result_code == 0:
                # Payment successful -> activate access
                order.transaction_id = receipt or order.transaction_id
                order.status = Order.Status.SUCCESS
                order.save(update_fields=["transaction_id", "status"])
                try:
                    order.activate_access()
                except Exception:
                    logger.exception("Error activating access for order %s", order.id)
            else:
                # Payment failed
                order.status = Order.Status.FAILED
                order.save(update_fields=["status"])

    except Exception:
        logger.exception("Error processing mpesa callback")

    return JsonResponse(daraja_ack)


# -------------------------
# Check film access (API)
# -------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def film_access_api(request, film_id):
    """
    Returns whether the authenticated user has access to the specified film.
    Response:
      { "access": true, "expires_at": "...", "stream_url": "/films/api/<id>/stream/" }
    """
    film = get_object_or_404(Film, id=film_id)

    order = Order.objects.filter(user=request.user, film=film, status=Order.Status.SUCCESS).first()
    if order and order.has_access():
        # If you have a FilmStreamView or HLS URL generator, return that instead of film.video_url
        stream_url = None
        try:
            # If your Film model stores an HLS path or you have a streaming endpoint, construct it here
            stream_url = request.build_absolute_uri(f"/films/api/{film.id}/stream/")
        except Exception:
            stream_url = None

        return Response({
            "access": True,
            "expires_at": order.access_expires_at.isoformat() if order.access_expires_at else None,
            "stream_url": stream_url,
        })

    return Response({"access": False})


# -------------------------
# Optional: Utility to create payouts (example)
# -------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payout(request):
    """
    Example endpoint to create a payout record for the authenticated filmmaker.
    This is a simple administrative helper; adapt access controls in production.
    """
    user = request.user
    amount_cents = int(request.data.get("amount_cents", 0))
    if amount_cents <= 0:
        return Response({"error": "amount_cents must be positive"}, status=400)

    payout = Payout.objects.create(
        filmmaker=user,
        amount_cents=amount_cents,
        status=Payout.Status.PENDING
    )

    return Response({"ok": True, "payout_id": payout.id, "status": payout.status})
