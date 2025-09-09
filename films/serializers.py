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
            "price_kes",
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


# --- THIS IS THE UPDATED SECTION ---
class FilmUploadSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    # We now expect the S3 key (a string) from the frontend, not the file itself.
    video_s3_key = serializers.CharField(write_only=True)

    class Meta:
        model = Film
        fields = [
            "title",
            "description",
            "release_date",
            "poster",
            "trailer_url",
            "video_s3_key", # Changed from 'video_file'
            "category",
            "price_kes",
        ]
    
    def create(self, validated_data):
        # The 'filmmaker' is added automatically in the view.
        # This will now correctly save the s3 key to your Film model.
        return Film.objects.create(**validated_data)


class RevenueSummarySerializer(serializers.Serializer):
    total_cents = serializers.IntegerField()
    pending_cents = serializers.IntegerField()
    per_film = serializers.ListField(child=serializers.DictField())
    payouts = serializers.ListField(child=serializers.DictField())