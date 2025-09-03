# analytics/serializers.py
from rest_framework import serializers

class EarningsSerializer(serializers.Serializer):
    """
    Serializer for summarizing a filmmaker's earnings.
    """
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_platform_fees = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_filmmaker_payout = serializers.DecimalField(max_digits=10, decimal_places=2)
    successful_sales_count = serializers.IntegerField()