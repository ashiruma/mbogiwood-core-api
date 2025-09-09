# payments/serializers.py
from django.conf import settings
from rest_framework import serializers
from .models import Order, Payout, PaymentTransaction, PayoutRequest
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
        read_only_fields = ["id", "status", "payment_id", "transaction_id", "created_at", "access_expires_at"]


class PayoutSerializer(serializers.ModelSerializer):
    filmmaker_name = serializers.CharField(source="filmmaker.get_full_name", read_only=True)

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
        read_only_fields = ["id", "filmmaker", "filmmaker_name", "status", "created_at", "completed_at"]


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
        read_only_fields = ["id", "created_at", "completed_at"]


class PayoutRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for filmmaker payout requests.
    - On create, the filmmaker is set from the request user (if provided in context).
    - Validates positive amount and optionally enforces a minimum payout if PAYOUT_MIN_CENTS is set in settings.
    """
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PayoutRequest
        fields = [
            "id",
            "filmmaker",
            "amount_cents",
            "mpesa_phone_number",
            "status",
            "status_display",
            "requested_at",
            "reviewed_at",
            "notes",
        ]
        read_only_fields = [
            "id",
            "filmmaker",
            "status",
            "status_display",
            "requested_at",
            "reviewed_at",
            "notes",
        ]

    def validate_amount_cents(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        min_cents = getattr(settings, "PAYOUT_MIN_CENTS", None)
        if min_cents is not None and value < min_cents:
            # Provide friendly message mentioning the configured minimum if present.
            readable_min = f"{min_cents / 100:.2f} KES" if isinstance(min_cents, int) else str(min_cents)
            raise serializers.ValidationError(f"Minimum payout is {readable_min}.")
        return value

    def create(self, validated_data):
        request = self.context.get("request", None)
        filmmaker = getattr(request, "user", None)
        # If view already sets filmmaker via perform_create, this will be redundant but safe.
        if filmmaker and not validated_data.get("filmmaker"):
            validated_data["filmmaker"] = filmmaker
        return super().create(validated_data)
