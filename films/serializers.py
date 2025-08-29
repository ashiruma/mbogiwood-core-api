# films/serializers.py
from rest_framework import serializers
from .models import Film, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class FilmSerializer(serializers.ModelSerializer):
    # This will now use the serializer above to show category details
    category = CategorySerializer(read_only=True)
    
    # We will rename trailer_url to match the frontend's expectation
    trailer_link = serializers.URLField(source='trailer_url')
    # We will rename poster to poster_image to match the frontend
    poster_image = serializers.ImageField(source='poster', read_only=True)

    class Meta:
        model = Film
        # These are the fields the frontend will receive
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "release_date", # Make sure to add this field to your view
            "poster_image",
            "trailer_link",
            "category",
        ]
