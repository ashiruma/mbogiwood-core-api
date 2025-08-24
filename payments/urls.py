from django.urls import path
from .views import CreateStripeCheckoutSession, payment_success, payment_cancel, watch_film
from .webhooks import stripe_webhook

urlpatterns = [
    path("stripe/create-checkout-session/<int:film_id>/", CreateStripeCheckoutSession.as_view(), name="stripe-create-checkout"),
    path("success/", payment_success, name="payment-success"),
    path("cancel/", payment_cancel, name="payment-cancel"),
    path("webhook/", stripe_webhook, name="stripe-webhook"),

    path("watch/<int:film_id>/", watch_film, name="watch-film"),

    path("pay/", views.initiate_payment, name="initiate_payment"),
    path("callback/", views.mpesa_callback, name="mpesa_callback"),
]
