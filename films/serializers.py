# films/serializers.py
from rest_framework import serializers
from .models import Film, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class FilmSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    trailer_link = serializers.URLField(source='trailer_url', read_only=True)
    poster_image = serializers.SerializerMethodField()

    class Meta:
        model = Film
        fields = [
            "id", "title", "slug", "description", "release_date",
            "poster_image", "trailer_link", "category", "price"
        ]

    def get_poster_image(self, obj):
        request = self.context.get('request')
        if obj.poster and hasattr(obj.poster, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.poster.url)
            return obj.poster.url
        return None

# --- SERIALIZER FOR THE UPLOAD VIEW ---
class FilmUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = [
            'title', 'description', 'price', 'video_file', 
            'poster', 'category', 'trailer_url', 'release_date'
        ]