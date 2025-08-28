from rest_framework import serializers
from .models import Film, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
        ]


class FilmSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # nested category info
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False
    )

    class Meta:
        model = Film
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "status",
            "price",
            "poster",
            "trailer_url",
            "video_file",
            "category",       # nested read
            "category_id",    # write-only, allows assigning by id
            "created_at",
            "updated_at",
        ]
