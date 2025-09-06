# FILE: films/views.py

from django.db.models import Sum
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import generics, permissions, status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from payments.models import Order, Payout
from .models import Film
from .serializers import FilmSerializer, FilmUploadSerializer, RevenueSummarySerializer


class IsFilmmaker(permissions.BasePermission):
    message = "You must be a registered filmmaker."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (getattr(request.user, "role", "") == "filmmaker" or getattr(request.user, "is_filmmaker", False))
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def film_list_api(request):
    promo_films = Film.objects.filter(status=Film.PROMO).order_by("-created_at")
    paid_films = Film.objects.filter(status=Film.PAID).order_by("-created_at")
    return Response(
        {
            "promo_films": FilmSerializer(promo_films, many=True, context={"request": request}).data,
            "paid_films": FilmSerializer(paid_films, many=True, context={"request": request}).data,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def film_detail_api(request, slug):
    film = get_object_or_404(Film, slug=slug)
    return Response(FilmSerializer(film, context={"request": request}).data)


class FilmUploadView(generics.CreateAPIView):
    queryset = Film.objects.all()
    serializer_class = FilmUploadSerializer
    permission_classes = [IsAuthenticated, IsFilmmaker]

    def perform_create(self, serializer):
        serializer.save(filmmaker=self.request.user)


class FilmmakerFilmListView(generics.ListAPIView):
    serializer_class = FilmSerializer
    permission_classes = [IsAuthenticated, IsFilmmaker]

    def get_queryset(self):
        return Film.objects.filter(filmmaker=self.request.user)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsFilmmaker])
def filmmaker_revenue_api(request):
    filmmaker = request.user

    total_revenue_cents = Order.objects.filter(
        film__filmmaker=filmmaker,
        status=Order.Status.SUCCESS
    ).aggregate(total=Sum('filmmaker_payout_cents'))['total'] or 0

    total_paid_out_cents = Payout.objects.filter(
        filmmaker=filmmaker,
        status=Payout.Status.COMPLETED
    ).aggregate(total=Sum('amount_cents'))['total'] or 0
    
    summary_data = {
        "total_revenue_cents": total_revenue_cents,
        "total_paid_out_cents": total_paid_out_cents,
        "current_balance_cents": total_revenue_cents - total_paid_out_cents,
    }
    
    serializer = RevenueSummarySerializer(summary_data)
    return Response(serializer.data)


def watch_film(request, slug):
    film = get_object_or_404(Film, slug=slug)
    unlocked = False

    if film.status == Film.PROMO:
        unlocked = True
    elif request.user.is_authenticated:
        is_owner = film.filmmaker == request.user
        has_access = Order.objects.filter(
            user=request.user,
            film=film,
            status=Order.Status.SUCCESS,
            access_expires_at__gt=timezone.now()
        ).exists()
        if is_owner or has_access:
            unlocked = True

    return render(request, "films/watch.html", {"film": film, "unlocked": unlocked})


class SecureFilmStreamView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        film = get_object_or_404(Film, pk=pk)

        # Check if the user has a valid, non-expired order for this film
        has_access = Order.objects.filter(
            user=request.user,
            film=film,
            status=Order.Status.SUCCESS,
            access_expires_at__gt=timezone.now()
        ).exists()

        if not has_access:
            return HttpResponseForbidden("You do not have permission to stream this film.")

        # If the user has access, return the path to the HLS manifest
        return Response({'hls_url': film.hls_manifest_path})
