from rest_framework import serializers
from .models import Film, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

class FilmSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Film
        fields = [
            "id", "title", "slug", "description", "status",
            "price", "poster", "trailer_url", "video_file",
            "category", "created_at", "updated_at"
        ]
