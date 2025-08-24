# payments/views.py
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
import stripe, json

from django.conf import settings
from films.models import Film
from .models import Order
from .utils import stk_push

stripe.api_key = settings.STRIPE_SECRET_KEY


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
def initiate_payment(request):
    film_id = request.data.get("film_id")
    phone = request.data.get("phone")

    film = get_object_or_404(Film, id=film_id, status=Film.PAID)

    # Create pending order
    order = Order.objects.create(
        user=request.user,
        film=film,
        payment_method=Order.MPESA,
        amount=film.price,
        currency="KES",
        status=Order.PENDING,
    )

    # Trigger STK push
    res = stk_push(phone, film.price, order_id=order.id)

    # Attach transaction ID if available
    checkout_id = res.get("CheckoutRequestID")
    if checkout_id:
        order.payment_id = checkout_id
        order.save(update_fields=["payment_id"])

    return Response(res)


@csrf_exempt
@api_view(["POST"])
def mpesa_callback(request):
    data = request.data
    stk_callback = data.get("Body", {}).get("stkCallback", {})
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    result_code = stk_callback.get("ResultCode")

    try:
        order = Order.objects.get(payment_id=checkout_request_id)
        if result_code == 0:
            order.activate_access()
        else:
            order.status = Order.FAILED
            order.save(update_fields=["status"])
    except Order.DoesNotExist:
        pass

    return Response({"ResultCode": 0, "ResultDesc": "Accepted"})
