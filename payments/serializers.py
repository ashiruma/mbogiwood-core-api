from rest_framework import serializers
from films.models import Film
from .models import Order

class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = ["id", "title", "description", "thumbnail", "trailer", "price", "status", "rental_period_days"]

class OrderSerializer(serializers.ModelSerializer):
    film = FilmSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "film", "payment_method", "payment_id", "amount", "currency", "status", "access_expires_at", "created_at"]
