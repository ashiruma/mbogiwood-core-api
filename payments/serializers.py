# payments/serializers.py
from rest_framework import serializers
from .models import Order, Payout, PaymentTransaction
from films.serializers import FilmSerializer # Import from the films app

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model, showing purchase details.
    """
    # Use the detailed FilmSerializer to show nested film info
    film = FilmSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "film",
            "amount_cents",
            "status",
            "created_at",
            "access_expires_at",
        ]

class PayoutSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payout model.
    """
    class Meta:
        model = Payout
        fields = "__all__"

class PaymentTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the PaymentTransaction model (M-Pesa logs).
    """
    class Meta:
        model = PaymentTransaction
        fields = "__all__"