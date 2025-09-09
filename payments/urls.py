# payments/urls.py
from django.urls import path
from . import views  # Import the entire views module

app_name = "payments"

urlpatterns = [
    # --- Healthcheck ---
    path("ping/", views.ping, name="ping"),

    # --- Stripe Endpoints ---
    path("stripe/create-session/<int:film_id>/", views.create_stripe_checkout_session, name="create-stripe-session"),
    path("stripe/success/", views.payment_success, name="payment-success"),
    path("stripe/cancel/", views.payment_cancel, name="payment-cancel"),

    # --- M-Pesa Payment Endpoints ---
    path("mpesa/initiate/", views.initiate_mpesa_payment, name="mpesa-initiate"),
    path("mpesa/callback/stk/", views.mpesa_stk_callback, name="mpesa-stk-callback"),

    # --- Payout Endpoints (Admin/System initiated) ---
    path("payouts/create/", views.create_payout, name="create-payout"),
    path("mpesa/callback/b2c-result/", views.mpesa_b2c_result, name="mpesa-b2c-result"),
    path("mpesa/callback/b2c-timeout/", views.mpesa_b2c_timeout, name="mpesa-b2c-timeout"),

    # --- Payout Request Endpoints (Filmmaker initiated) ---
    path("payout-requests/", views.PayoutRequestListView.as_view(), name="payout-request-list"),
    path("payout-requests/create/", views.PayoutRequestCreateView.as_view(), name="payout-request-create"),

    # --- Film Access API ---
    path("film-access/<int:film_id>/", views.film_access_api, name="film-access-api"),
]