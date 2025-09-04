from rest_framework import serializers
from films.models import Film
from payments.models import Payout, Order
from .models import FilmmakerApplication 

# Serializer for individual film performance stats
class FilmPerformanceSerializer(serializers.ModelSerializer):
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_sales = serializers.IntegerField()

    class Meta:
        model = Film
        fields = ['id', 'title', 'cover_image', 'release_date', 'total_revenue', 'total_sales']

# Serializer for payout history
class PayoutHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = ['id', 'amount', 'status', 'created_at']

# Main serializer for the entire dashboard
class FilmmakerDashboardSerializer(serializers.Serializer):
    # Summary Stats
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_paid_out = serializers.DecimalField(max_digits=12, decimal_places=2)
    current_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Detailed Lists
    film_performance = FilmPerformanceSerializer(many=True)
    payout_history = PayoutHistorySerializer(many=True)

class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and viewing a filmmaker application.
    """
    class Meta:
        model = FilmmakerApplication
        # List the fields a user should submit in their application
        fields = ['reasons', 'previous_works_links', 'showreel_link']
