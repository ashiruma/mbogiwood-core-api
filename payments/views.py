import json
import logging
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.urls import reverse

from films.models import Film
from .models import Order, PaymentTransaction, Payout
from .utils import stk_push  # helper for Daraja / STK push

logger = logging.getLogger(__name__)
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)


# -------------------------
# Healthcheck
# -------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def ping(request):
    return Response({"status": "ok", "app": "payments"})


# -------------------------
# Stripe Checkout Session
# -------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_stripe_checkout_session(request, film_id):
    film = get_object_or_404(Film, id=film_id, status=Film.PAID)

    order = Order.objects.create(
        user=request.user,
        film=film,
        payment_method=Order.PaymentMethod.STRIPE,
        amount_cents=int(film.price * 100),  # ✅ FIXED
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
    return render(request, "payments/success.html", {"session_id": request.GET.get("session_id")})


def payment_cancel(request):
    return render(request, "payments/cancel.html")


# -------------------------
# M-Pesa Payment
# -------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_mpesa_payment(request):
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
        amount_cents=int(film.price * 100),  # ✅ FIXED
        currency=getattr(film, "currency", "KES"),
        status=Order.Status.PENDING,
        phone_number=phone,
    )

    try:
        res = stk_push(phone=phone, amount_cents=order.amount_cents, order_id=order.id)
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
def mpesa_callback(request):
    payload = request.data if hasattr(request, "data") else json.loads(request.body.decode("utf-8"))
    logger.info("M-Pesa Callback payload: %s", json.dumps(payload))

    stk = payload.get("Body", {}).get("stkCallback", {}) if isinstance(payload, dict) else {}
    checkout_request_id = stk.get("CheckoutRequestID")
    result_code = stk.get("ResultCode")
    result_desc = stk.get("ResultDesc")

    payment_txn = PaymentTransaction.objects.filter(
        checkout_request_id=checkout_request_id
    ).first() if checkout_request_id else None

    daraja_ack = {"ResultCode": 0, "ResultDesc": "Accepted"}
    if not checkout_request_id:
        return JsonResponse(daraja_ack)

    # Parse metadata
    callback_items = stk.get("CallbackMetadata", {}).get("Item", []) or []
    receipt, amount, phone = None, None, None
    for item in callback_items:
        name, val = item.get("Name"), item.get("Value")
        if name == "MpesaReceiptNumber":
            receipt = val
        elif name == "Amount":
            amount = val
        elif name == "PhoneNumber":
            phone = val

    try:
        if payment_txn:
            payment_txn.result_desc = result_desc
            payment_txn.result_code = result_code
            if receipt:
                payment_txn.mpesa_receipt = receipt
            if amount:
                payment_txn.amount_cents = int(float(amount) * 100)
            if phone:
                payment_txn.phone_number = phone
            payment_txn.status = "SUCCESS" if result_code == 0 else "FAILED"
            payment_txn.completed_at = timezone.now()
            payment_txn.save()

        order = Order.objects.filter(payment_id=checkout_request_id).first()
        if not order and phone:
            order = Order.objects.filter(
                phone_number=phone, status=Order.Status.PENDING
            ).order_by("-created_at").first()

        if order:
            if result_code == 0:
                order.transaction_id = receipt or order.transaction_id
                order.activate_access()  # ✅ handles SUCCESS + expiry
            else:
                order.status = Order.Status.FAILED
                order.save(update_fields=["status"])

    except Exception:
        logger.exception("Error processing mpesa callback")

    return JsonResponse(daraja_ack)


# -------------------------
# Check Film Access
# -------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def film_access_api(request, film_id):
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


# -------------------------
# Payouts
# -------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payout(request):
    amount_cents = int(request.data.get("amount_cents", 0))
    if amount_cents <= 0:
        return Response({"error": "amount_cents must be positive"}, status=400)

    payout = Payout.objects.create(
        filmmaker=request.user,
        amount_cents=amount_cents,
        status=Payout.Status.PENDING,
    )

    return Response({"ok": True, "payout_id": payout.id, "status": payout.status})
