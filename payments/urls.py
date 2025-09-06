# payments/urls.py
from django.urls import path
from .views import (
    initiate_mpesa_payment,
    mpesa_callback,
    create_stripe_checkout_session,  # ✅ fixed
    payment_success,
    payment_cancel,
    film_access_api,
    create_payout,
)

app_name = "payments"

urlpatterns = [
    # --- M-Pesa Endpoints ---
    path("mpesa/initiate/", initiate_mpesa_payment, name="initiate-mpesa-payment"),
    path("mpesa/callback/", mpesa_callback, name="mpesa-callback"),

    # --- Stripe Endpoints ---
    path("stripe/create-session/<int:film_id>/", create_stripe_checkout_session, name="create-stripe-session"),
    path("stripe/success/", payment_success, name="payment-success"),
    path("stripe/cancel/", payment_cancel, name="payment-cancel"),

    # --- Film Access ---
    path("film/<int:film_id>/access/", film_access_api, name="film-access-api"),

    # --- Payouts ---
    path("payout/create/", create_payout, name="create-payout"),
]
