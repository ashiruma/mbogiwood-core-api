# films/serializers.py
from rest_framework import serializers
from .models import Film, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class FilmSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    poster_url = serializers.SerializerMethodField()
    filmmaker_name = serializers.SerializerMethodField()

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
            "price_kes",   # ✅ use price_kes (consistent with payments app)
            "filmmaker_name",
        ]

    def get_poster_url(self, obj):
        request = self.context.get("request")
        if obj.poster and hasattr(obj.poster, "url"):
            return request.build_absolute_uri(obj.poster.url) if request else obj.poster.url
        return None

    def get_filmmaker_name(self, obj):
        if hasattr(obj.filmmaker, "get_full_name") and obj.filmmaker.get_full_name():
            return obj.filmmaker.get_full_name()
        if hasattr(obj.filmmaker, "username"):
            return obj.filmmaker.username
        return "Mbogiwood Productions"


class FilmUploadSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Film
        fields = [
            "title",
            "description",
            "release_date",
            "poster",
            "trailer_url",
            "video_file",
            "category",
            "price_kes",   # ✅ use price_kes
        ]


class RevenueSummarySerializer(serializers.Serializer):
    total_cents = serializers.IntegerField()
    pending_cents = serializers.IntegerField()
    per_film = serializers.ListField(child=serializers.DictField())
    payouts = serializers.ListField(child=serializers.DictField())
