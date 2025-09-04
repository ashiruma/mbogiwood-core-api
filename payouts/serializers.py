from rest_framework import serializers
from .models import Payout


class PayoutSerializer(serializers.ModelSerializer):
class Meta:
model = Payout
fields = ["id", "amount_cents", "method", "status", "requested_at", "processed_at", "reference"]
read_only_fields = ["status", "requested_at", "processed_at", "reference"]