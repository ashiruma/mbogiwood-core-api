# films/serializers.py
from rest_framework import serializers
from .models import Film, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class FilmSerializer(serializers.ModelSerializer):
    # This will use the serializer above to show category details
    category = CategorySerializer(read_only=True)
    
    # We rename `trailer_url` from the model to `trailer_link` to match the frontend
    trailer_link = serializers.URLField(source='trailer_url', read_only=True)
    
    # We rename `poster` from the model to `poster_image` and build the full URL
    poster_image = serializers.SerializerMethodField()

    class Meta:
        model = Film
        # These are the fields the frontend will receive
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "release_date",
            "poster_image",
            "trailer_link",
            "category",
        ]

    def get_poster_image(self, obj):
        request = self.context.get('request')
        if obj.poster and hasattr(obj.poster, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.poster.url)
            return obj.poster.url
        return None
