# payments/urls.py
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("", views.ping, name="payments-root"),  # root endpoint for /api/payments/
    path("ping/", views.ping, name="payments-ping"),
    path("pay/", views.initiate_payment, name="initiate_payment"),
    path("mpesa-callback/", views.mpesa_callback, name="mpesa_callback"),
    path("stripe/create-session/<int:film_id>/", views.CreateStripeCheckoutSession.as_view(), name="create_stripe_session"),
    path("success/", views.payment_success, name="payment_success"),
    path("cancel/", views.payment_cancel, name="payment_cancel"),
]
