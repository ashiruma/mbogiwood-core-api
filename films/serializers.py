# films/serializers.py
from rest_framework import serializers
from .models import Film, Category

# ===================================================================
# --- Reusable Model Serializers ---
# ===================================================================

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model, for nested display within films.
    """
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

class FilmSerializer(serializers.ModelSerializer):
    """
    The main serializer for displaying Film details to the public.
    """
    category = CategorySerializer(read_only=True)
    poster_url = serializers.SerializerMethodField()
    filmmaker_name = serializers.CharField(source='filmmaker.get_full_name', read_only=True, default='Mbogiwood Productions')

    class Meta:
        model = Film
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "release_date",
            "poster_url",
            "trailer_url",
            "category",
            "price_cents", # Standardized to use cents
            "filmmaker_name",
        ]

    def get_poster_url(self, obj):
        """
        Returns the absolute URL for the poster image.
        """
        request = self.context.get('request')
        if obj.poster and hasattr(obj.poster, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.poster.url)
            return obj.poster.url
        return None

# ===================================================================
# --- Serializers for Specific Actions ---
# ===================================================================

class FilmUploadSerializer(serializers.ModelSerializer):
    """
    Serializer used specifically for validating and creating new film uploads.
    """
    # For write operations, sending just the ID of the category is more efficient.
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Film
        fields = [
            'title',
            'description',
            'release_date',
            'poster',
            'trailer_url',
            'video_file',
            'category',
            'price_cents', # Standardized to use cents
        ]

class RevenueSummarySerializer(serializers.Serializer):
    """
    A non-model serializer for structuring the filmmaker's revenue data.
    """
    total_cents = serializers.IntegerField()
    pending_cents = serializers.IntegerField()
    per_film = serializers.ListField(child=serializers.DictField())
    payouts = serializers.ListField(child=serializers.DictField())