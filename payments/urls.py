# ===================================================================
# --- IMPORTS ---
# ===================================================================
from django.urls import path
from .views import (
    initiate_mpesa_payment,
    mpesa_callback,
    CreateStripeCheckoutSession,
    payment_success,
    payment_cancel,
    watch_film,
    film_access_api,
    create_payout,
)

app_name = "payments"

# ===================================================================
# --- URL PATTERNS ---
# ===================================================================
urlpatterns = [
    # --- M-Pesa Endpoints ---
    path("mpesa/initiate/", initiate_mpesa_payment, name="initiate-mpesa-payment"),
    path("mpesa/callback/", mpesa_callback, name="mpesa-callback"),

    # --- Stripe Endpoints ---
    path("stripe/create-session/<int:film_id>/", CreateStripeCheckoutSession.as_view(), name="create-stripe-session"),
    path("stripe/success/", payment_success, name="payment-success"),
    path("stripe/cancel/", payment_cancel, name="payment-cancel"),

    # --- Film Access & Watch ---
    path("film/<int:film_id>/access/", film_access_api, name="film-access-api"),
    path("film/<int:film_id>/watch/", watch_film, name="watch-film"),

    # --- Payouts ---
    path("payout/create/", create_payout, name="create-payout"),
]
