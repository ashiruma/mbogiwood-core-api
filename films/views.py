# films/views.py
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.generic import ListView

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Film, Category
from payments.models import Order
from .serializers import FilmSerializer, FilmUploadSerializer


# ===================================================================
# --- FILM UPLOAD LOGIC ---
# ===================================================================
class IsFilmmaker(permissions.BasePermission):
    message = "You do not have permission to perform this action. Only filmmakers can upload."
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (getattr(request.user, 'role', '') == 'filmmaker' or getattr(request.user, 'is_filmmaker', False))

class FilmUploadView(generics.CreateAPIView):
    queryset = Film.objects.all()
    serializer_class = FilmUploadSerializer
    permission_classes = [IsFilmmaker]

    def perform_create(self, serializer):
        serializer.save(filmmaker=self.request.user)

# ===================================================================
# --- NEW VIEW FOR FILMMAKER DASHBOARD ---
# ===================================================================
class FilmmakerFilmListView(generics.ListAPIView):
    """
    API view for a filmmaker to see a list of their own uploaded films.
    """
    serializer_class = FilmSerializer
    permission_classes = [IsAuthenticated, IsFilmmaker]

    def get_queryset(self):
        """
        This view returns a list of all the films
        for the currently authenticated filmmaker.
        """
        user = self.request.user
        return Film.objects.filter(filmmaker=user)
# ===================================================================


# ===================================================================
# --- PUBLIC API ENDPOINTS ---
# ===================================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def film_list_api(request):
    promo_films_qs = Film.objects.filter(status=Film.PROMO).order_by('-created_at')
    paid_films_qs = Film.objects.filter(status=Film.PAID).order_by('-created_at')
    promo_films_serializer = FilmSerializer(promo_films_qs, many=True, context={'request': request})
    paid_films_serializer = FilmSerializer(paid_films_qs, many=True, context={'request': request})
    return Response({
        'promo_films': promo_films_serializer.data,
        'paid_films': paid_films_serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def film_detail_api(request, slug):
    film = get_object_or_404(Film, slug=slug)
    serializer = FilmSerializer(film, context={'request': request})
    return Response(serializer.data)

# ===================================================================
# --- PAGE RENDERING & STRIPE PAYMENT LOGIC ---
# ===================================================================
def dev_dashboard(request):
    return render(request, 'dashboard.html')

def watch_film(request, slug):
    film = get_object_or_404(Film, slug=slug)
    unlocked = False
    if request.user.is_authenticated:
        unlocked = Order.objects.filter(
            user=request.user, film=film, 
            status=Order.SUCCESS, access_expires_at__gt=timezone.now()
        ).exists()
    if film.status == Film.PROMO:
        unlocked = True
    return render(request, 'watch.html', {'film': film, 'unlocked': unlocked})

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, slug):
    film = get_object_or_404(Film, slug=slug, status=Film.PAID)
    success_url = request.build_absolute_uri(reverse('films:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}'
    cancel_url = request.build_absolute_uri(reverse('films:payment_cancel'))
    order = Order.objects.create(
        user=request.user, film=film, 
        payment_method=Order.STRIPE, amount=film.price, status=Order.PENDING
    )
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'kes', 
                    'product_data': {'name': film.title},
                    'unit_amount': int(film.price * 100)
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
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return HttpResponse(status=400)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id, status=Order.PENDING)
                order.activate_access()
            except Order.DoesNotExist:
                return HttpResponse(status=404)
    return HttpResponse(status=200)

def payment_success(request):
    return render(request, 'success.html', {'session_id': request.GET.get('session_id')})

def payment_cancel(request):
    return render(request, 'cancel.html')