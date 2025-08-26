# payments/views.py
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
import stripe, json, logging
from django.http import JsonResponse

from django.conf import settings
from films.models import Film
from .models import Order, PaymentTransaction
from .utils import stk_push

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

def ping(request):
    """A simple view to confirm the payments app is responsive."""
    return JsonResponse({"status": "ok", "app": "payments"})

class CreateStripeCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, film_id):
        film = get_object_or_404(Film, id=film_id, status=Film.PAID)

        order = Order.objects.create(
            user=request.user,
            film=film,
            payment_method=Order.STRIPE,
            amount=film.price,
            currency="USD",
            status=Order.PENDING,
        )

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": film.title},
                    "unit_amount": int(film.price * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(f"/payments/success/?session_id={{CHECKOUT_SESSION_ID}}"),
            cancel_url=request.build_absolute_uri("/payments/cancel/"),
            metadata={"order_id": str(order.id)},
        )

        order.payment_id = session.id
        order.save(update_fields=["payment_id"])

        return Response({"id": session.id, "checkout_url": session.url})


@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")
    return render(request, "payments/success.html", {"session_id": session_id})


@login_required
def payment_cancel(request):
    return render(request, "payments/cancel.html")


@login_required
def watch_film(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    if film.status == Film.PROMO:
        return render(request, "films/watch.html", {"film": film, "unlocked": True})

    has_access = Order.objects.filter(
        user=request.user,
        film=film,
        status=Order.SUCCESS,
        access_expires_at__gt=timezone.now()
    ).exists()

    return render(request, "films/watch.html", {"film": film, "unlocked": has_access})


# --- M-Pesa STK Push ---
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    film_id = request.data.get("film_id")
    phone = request.data.get("phone")

    film = get_object_or_404(Film, id=film_id, status=Film.PAID)

    order = Order.objects.create(
        user=request.user,
        film=film,
        payment_method=Order.MPESA,
        amount=film.price,
        currency="KES",
        status=Order.PENDING,
    )

    res = stk_push(phone, film.price, order_id=order.id)

    checkout_id = res.get("CheckoutRequestID")
    if checkout_id:
        order.payment_id = checkout_id
        order.save(update_fields=["payment_id"])

        PaymentTransaction.objects.create(
            phone_number=phone,
            amount=film.price,
            checkout_request_id=checkout_id,
            status="PENDING"
        )

    return Response(res)


@csrf_exempt
@api_view(["POST"])
def mpesa_callback(request):
    logger.info("M-Pesa Callback: %s", json.dumps(request.data))
    data = request.data
    stk_callback = data.get("Body", {}).get("stkCallback", {})
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    result_code = stk_callback.get("ResultCode")
    result_desc = stk_callback.get("ResultDesc")

    try:
        order = Order.objects.get(payment_id=checkout_request_id)
        payment_txn = PaymentTransaction.objects.filter(checkout_request_id=checkout_request_id).first()

        if result_code == 0:
            metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            receipt_number, amount, phone = None, None, None

            for item in metadata:
                if item["Name"] == "MpesaReceiptNumber":
                    receipt_number = item["Value"]
                elif item["Name"] == "Amount":
                    amount = item["Value"]
                elif item["Name"] == "PhoneNumber":
                    phone = item["Value"]

            order.activate_access()
            if payment_txn:
                payment_txn.status = "SUCCESS"
                payment_txn.receipt_number = receipt_number
                payment_txn.amount = amount
                payment_txn.phone_number = phone
                payment_txn.result_desc = result_desc
                payment_txn.save()

        else:
            order.status = Order.FAILED
            order.save(update_fields=["status"])
            if payment_txn:
                payment_txn.status = "FAILED"
                payment_txn.result_desc = result_desc
                payment_txn.save()

    except Order.DoesNotExist:
        pass

    return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


class STKPushView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        amount = request.data.get("amount")
        resp = stk_push(phone, amount)
        return Response(resp)
def ping(request):
    return JsonResponse({"status": "ok", "app": "payments"})