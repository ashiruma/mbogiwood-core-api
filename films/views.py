# films/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Film
from .serializers import FilmSerializer

# --- Your other imports and views can remain the same ---


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


# --- You can keep all your other views below this ---
# (dev_dashboard, payment_success, etc.)
