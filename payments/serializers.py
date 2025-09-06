from rest_framework import serializers
from .models import Order, Payout, PaymentTransaction
from films.serializers import FilmSerializer


class OrderSerializer(serializers.ModelSerializer):
    film = FilmSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "film",
            "payment_method",
            "amount_cents",
            "currency",
            "status",
            "payment_id",
            "transaction_id",
            "phone_number",
            "created_at",
            "access_expires_at",
        ]


class PayoutSerializer(serializers.ModelSerializer):
    filmmaker_name = serializers.CharField(
        source="filmmaker.get_full_name", read_only=True
    )

    class Meta:
        model = Payout
        fields = [
            "id",
            "filmmaker",
            "filmmaker_name",
            "amount_cents",
            "status",
            "transaction_id",
            "created_at",
            "completed_at",
        ]


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "checkout_request_id",
            "merchant_request_id",
            "result_code",
            "result_desc",
            "amount_cents",
            "mpesa_receipt",
            "phone_number",
            "status",
            "created_at",
            "completed_at",
        ]
