# films/views.py
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.generic import ListView, DetailView

# --- ADDED IMPORTS ---
from rest_framework.decorators import api_view
from rest_framework.response import Response
# -------------------

from .models import Film, Category, Order
from .serializers import FilmSerializer


# --- REVISED Main JSON API Endpoint for Frontend ---
@api_view(['GET'])
def film_list_api(request):
    """
    Provides a list of promotional and paid films,
    formatted by the FilmSerializer.
    """
    # Get the full objects from the database
    promo_films_qs = Film.objects.filter(status=Film.PROMO).order_by('-created_at')
    paid_films_qs = Film.objects.filter(status=Film.PAID).order_by('-created_at')

    # Use the serializer to convert the objects to JSON
    promo_films_serializer = FilmSerializer(promo_films_qs, many=True, context={'request': request})
    paid_films_serializer = FilmSerializer(paid_films_qs, many=True, context={'request': request})

    data = {
        'promo_films': promo_films_serializer.data,
        'paid_films': paid_films_serializer.data
    }
    return Response(data)


# --- Page Rendering & Supporting Views ---
def dev_dashboard(request):
    return render(request, 'dashboard.html')

def payment_success(request):
    return render(request, 'success.html', {'session_id': request.GET.get('session_id')})

def payment_cancel(request):
    return render(request, 'cancel.html')

def watch_film(request, slug):
    film = get_object_or_404(Film, slug=slug)
    unlocked = False
    if request.user.is_authenticated:
        unlocked = Order.objects.filter(user=request.user, film=film, status=Order.SUCCESS, access_expires_at__gt=timezone.now()).exists()
    
    if film.status == Film.PROMO:
        unlocked = True
        
    return render(request, 'watch.html', {'film': film, 'unlocked': unlocked})


# --- Payment Logic ---
# Note: Your Stripe logic is commented out until you configure it
# stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, slug):
    film = get_object_or_404(Film, slug=slug, status=Film.PAID)
    success_url = request.build_absolute_uri(reverse('films:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}'
    cancel_url = request.build_absolute_uri(reverse('films:payment_cancel'))
    order = Order.objects.create(user=request.user, film=film, payment_method=Order.STRIPE, amount=film.price, status=Order.PENDING)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': film.title}, 'unit_amount': int(film.price * 100)}, 'quantity': 1}],
            mode='payment', success_url=success_url, cancel_url=cancel_url, metadata={'order_id': order.id}
        )
        order.payment_id = checkout_session.id
        order.save()
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def stripe_webhook(request):
    payload, sig_header = request.body, request.META.get('HTTP_STRIPE_SIGNATURE')
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
                order.activate_access()
            except Order.DoesNotExist:
                return HttpResponse(status=404)
    return HttpResponse(status=200)


# --- Old JSON API Views (Can be removed if not used elsewhere) ---
def ping(request):
    return JsonResponse({"status": "ok", "app": "films"})

class CategoryListView(ListView):
    model = Category
    def render_to_response(self, context, **response_kwargs):
        return JsonResponse([{"id": c.id, "name": c.name, "slug": c.slug} for c in context["object_list"]], safe=False)

class FilmListView(ListView):
    model = Film
    def render_to_response(self, context, **response_kwargs):
        return JsonResponse([{"id": f.id, "title": f.title, "slug": f.slug} for f in context["object_list"]], safe=False)
