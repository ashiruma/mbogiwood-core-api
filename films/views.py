# films/views.py

# ===================================================================
# --- 1. IMPORTS ---
# ===================================================================
# Standard Library
from datetime import timedelta

# Third-Party Imports
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# Local Application Imports
from payments.models import Order
from .models import Film, Category
from .serializers import (
    FilmSerializer,
    FilmUploadSerializer,
    RevenueSummarySerializer # Assuming this serializer exists
)


# ===================================================================
# --- 2. CUSTOM PERMISSIONS ---
# ===================================================================

class IsFilmmaker(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'filmmaker' role.
    """
    message = "You must be a registered filmmaker to perform this action."

    def has_permission(self, request, view):
        # Checks if the user is authenticated and has the filmmaker role or flag.
        return request.user and request.user.is_authenticated and (
            getattr(request.user, 'role', '') == 'filmmaker' or
            getattr(request.user, 'is_filmmaker', False)
        )

class CanStreamFilm(permissions.BasePermission):
    """
    Custom permission to check if a user can stream a specific film.
    - The film's owner can always stream.
    - A user with a valid, non-expired transaction can stream.
    """
    message = "You do not have permission to stream this film."

    def has_object_permission(self, request, view, obj):
        # 'obj' is the Film instance.
        user = request.user

        # Rule 1: The filmmaker who owns the film can always stream.
        if obj.filmmaker == user:
            return True

        # Rule 2: Check for a valid, non-expired transaction for this film.
        return Transaction.objects.filter(
            film=obj,
            buyer=user,
            access_expires_at__gt=timezone.now()
        ).exists()


# ===================================================================
# --- 3. API VIEWS (DJANGO REST FRAMEWORK) ---
# ===================================================================

# --- Public API Endpoints ---

@api_view(['GET'])
@permission_classes([AllowAny])
def film_list_api(request):
    """
    Provides a list of all promo and paid films for public consumption.
    """
    promo_films = Film.objects.filter(status=Film.PROMO).order_by('-created_at')
    paid_films = Film.objects.filter(status=Film.PAID).order_by('-created_at')

    promo_serializer = FilmSerializer(promo_films, many=True, context={'request': request})
    paid_serializer = FilmSerializer(paid_films, many=True, context={'request': request})

    return Response({
        'promo_films': promo_serializer.data,
        'paid_films': paid_serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def film_detail_api(request, slug):
    """
    Provides detailed information for a single film, identified by its slug.
    """
    film = get_object_or_404(Film, slug=slug)
    serializer = FilmSerializer(film, context={'request': request})
    return Response(serializer.data)


# --- Filmmaker-Specific API Endpoints ---

class FilmUploadView(generics.CreateAPIView):
    """
    Allows authenticated filmmakers to upload a new film.
    """
    queryset = Film.objects.all()
    serializer_class = FilmUploadSerializer
    permission_classes = [IsAuthenticated, IsFilmmaker]

    def perform_create(self, serializer):
        # Automatically assign the logged-in filmmaker to the film.
        serializer.save(filmmaker=self.request.user)

class FilmmakerFilmListView(generics.ListAPIView):
    """
    Provides a filmmaker with a list of their own uploaded films.
    """
    serializer_class = FilmSerializer
    permission_classes = [IsAuthenticated, IsFilmmaker]

    def get_queryset(self):
        # Filter films to return only those owned by the current user.
        return Film.objects.filter(filmmaker=self.request.user)

class FilmStreamView(views.APIView):
    """
    Provides a secure, signed HLS manifest URL for a film.
    Permission is checked by the CanStreamFilm class.
    """
    permission_classes = [IsAuthenticated, CanStreamFilm]

    def get(self, request, pk):
        film = get_object_or_404(Film, pk=pk)
        self.check_object_permissions(request, film) # Check permissions against the film object

        if not film.hls_manifest_path:
            return Response({"detail": "This film is not yet available for streaming."}, status=status.HTTP_404_NOT_FOUND)

        # NOTE: The sign_url function is not defined here, assuming it exists elsewhere.
        # Example: from your_utils_folder import sign_url
        base_url = request.build_absolute_uri("/").rstrip("/")
        manifest_url = f"{base_url}{film.hls_manifest_path}"
        signed_url = sign_url(manifest_url, ttl_seconds=3600) # Assumes a signing function

        return Response({
            "hls": signed_url,
            "watermark": request.user.email or request.user.username
        })

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsFilmmaker])
def filmmaker_revenue_api(request):
    """
    Calculates and returns the revenue summary for the logged-in filmmaker.
    """
    user = request.user
    films = Film.objects.filter(filmmaker=user) # Standardized to 'filmmaker'
    film_ids = films.values_list("id", flat=True)
    transactions = Transaction.objects.filter(film_id__in=film_ids)

    total_gross_cents = sum(t.amount_cents for t in transactions)
    filmmaker_total_cents = int(total_gross_cents * 0.7) # 70% cut

    # TODO: Add logic to subtract paid amounts from a Payout model
    pending_cents = filmmaker_total_cents

    per_film_revenue = []
    for film in films:
        film_transactions = [t for t in transactions if t.film_id == film.id]
        gross_cents = sum(t.amount_cents for t in film_transactions)
        per_film_revenue.append({
            "film_id": film.id,
            "title": film.title,
            "gross_cents": gross_cents,
            "filmmaker_cents": int(gross_cents * 0.7),
        })

    data = {
        "total_cents": filmmaker_total_cents,
        "pending_cents": pending_cents,
        "per_film": per_film_revenue,
        "payouts": [], # Placeholder for payout history
    }
    serializer = RevenueSummarySerializer(data)
    return Response(serializer.data)


# ===================================================================
# --- 4. PAYMENT PROCESSING & WEBHOOKS ---
# ===================================================================

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, slug):
    """
    Creates a Stripe Checkout session for purchasing a film.
    """
    film = get_object_or_404(Film, slug=slug, status=Film.PAID)
    success_url = request.build_absolute_uri(reverse('films:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}'
    cancel_url = request.build_absolute_uri(reverse('films:payment_cancel'))

    order = Order.objects.create(
        user=request.user,
        film=film,
        payment_method=Order.STRIPE,
        amount=film.price,
        status=Order.PENDING
    )

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'kes',
                    'product_data': {'name': film.title},
                    'unit_amount': int(film.price * 100) # Stripe expects amount in cents
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'order_id': order.id}
        )
        order.payment_id = checkout_session.id
        order.save()
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def stripe_webhook(request):
    """
    Handles incoming webhooks from Stripe to confirm payment success.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id, status=Order.PENDING)
                order.activate_access() # Assumes a method on the Order model
            except Order.DoesNotExist:
                return HttpResponse(status=404)
    return HttpResponse(status=200)


# ===================================================================
# --- 5. TEMPLATE RENDERING VIEWS (STANDARD DJANGO) ---
# ===================================================================

def watch_film(request, slug):
    """
    Renders the page for watching a specific film.
    Checks if the user has unlocked access to the film.
    """
    film = get_object_or_404(Film, slug=slug)
    unlocked = False

    if film.status == Film.PROMO:
        unlocked = True
    elif request.user.is_authenticated:
        # Check for a successful order with non-expired access
        unlocked = Order.objects.filter(
            user=request.user,
            film=film,
            status=Order.SUCCESS,
            access_expires_at__gt=timezone.now()
        ).exists()

    return render(request, 'watch.html', {'film': film, 'unlocked': unlocked})

def payment_success(request):
    """
    Renders the success page after a successful Stripe payment.
    """
    return render(request, 'success.html', {'session_id': request.GET.get('session_id')})

def payment_cancel(request):
    """
    Renders the cancellation page after a cancelled Stripe payment.
    """
    return render(request, 'cancel.html')

def dev_dashboard(request):
    """
    A simple view for rendering a development or test dashboard.
    """
    return render(request, 'dashboard.html')