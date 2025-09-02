# gallery/serializers.py
from rest_framework import serializers
from .models import GalleryImage

class GalleryImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = GalleryImage
        fields = ['id', 'title', 'description', 'image_url', 'uploaded_at']