# analytics/views.py
from django.db.models import Sum, Count
from rest_framework import views, response, permissions
from payments.models import Order
from films.views import IsFilmmaker # Re-using our IsFilmmaker permission
from .serializers import EarningsSerializer

class FilmmakerEarningsView(views.APIView):
    """
    Provides a summary of earnings for the currently authenticated filmmaker.
    """
    permission_classes = [permissions.IsAuthenticated, IsFilmmaker]

    def get(self, request, *args, **kwargs):
        filmmaker = self.request.user
        
        # Query all successful orders for the filmmaker's films
        queryset = Order.objects.filter(
            film__filmmaker=filmmaker, 
            status=Order.SUCCESS
        )
        
        # Aggregate the data
        aggregates = queryset.aggregate(
            total_revenue=Sum('amount'),
            total_platform_fees=Sum('platform_fee'),
            total_filmmaker_payout=Sum('filmmaker_payout'),
            successful_sales_count=Count('id')
        )

        # Handle case where there are no sales yet
        for key, value in aggregates.items():
            if value is None:
                aggregates[key] = 0

        serializer = EarningsSerializer(aggregates)
        return response.Response(serializer.data)