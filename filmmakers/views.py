# filmmakers/views.py

from django.db.models import Sum, Count, Q
from rest_framework import generics, permissions, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from films.models import Film
from payments.models import Payout, Order
from .models import FilmmakerApplication
from .serializers import ApplicationSerializer, FilmmakerDashboardSerializer


class FilmmakerDashboardView(views.APIView):
    """
    Provides all necessary data for the filmmaker's dashboard,
    including revenue stats, film performance, and payout history.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        filmmaker = request.user

        # 1. Calculate Summary Stats using the 'Order' model and '_cents' fields
        total_revenue_cents = Order.objects.filter(
            film__filmmaker=filmmaker,
            status=Order.Status.SUCCESS  # Only count successful orders
        ).aggregate(total=Sum('filmmaker_payout_cents'))['total'] or 0

        total_paid_out_cents = Payout.objects.filter(
            filmmaker=filmmaker,
            status=Payout.Status.COMPLETED
        ).aggregate(total=Sum('amount_cents'))['total'] or 0

        current_balance_cents = total_revenue_cents - total_paid_out_cents

        # 2. Get Film Performance Stats
        films = Film.objects.filter(filmmaker=filmmaker).annotate(
            total_revenue_cents=Sum(
                'orders__filmmaker_payout_cents',
                filter=Q(orders__status=Order.Status.SUCCESS)
            ),
            total_sales=Count(
                'orders',
                filter=Q(orders__status=Order.Status.SUCCESS)
            )
        ).order_by('-total_revenue_cents')

        # 3. Get Payout History
        payouts = Payout.objects.filter(filmmaker=filmmaker).order_by('-created_at')

        # 4. Prepare data for the serializer
        dashboard_data = {
            'total_revenue_cents': total_revenue_cents,
            'total_paid_out_cents': total_paid_out_cents,
            'current_balance_cents': current_balance_cents,
            'film_performance': films,
            'payout_history': payouts,
        }

        # Note: Ensure your FilmmakerDashboardSerializer expects '_cents' fields
        serializer = FilmmakerDashboardSerializer(instance=dashboard_data)
        return Response(serializer.data)


class ApplicationCreateView(generics.CreateAPIView):
    """
    Handles the creation of a new filmmaker application.
    """
    queryset = FilmmakerApplication.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Automatically associates the application with the logged-in user.
        """
        serializer.save(user=self.request.user)