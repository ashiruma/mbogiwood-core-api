from rest_framework import serializers
from .models import Film, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

class FilmSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # show category details

    class Meta:
        model = Film
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "poster",
            "trailer_url",
            "video_file",
            "price",
            "rental_period_days",
            "status",
            "category",
            "created_at",
            "updated_at",
        ]
