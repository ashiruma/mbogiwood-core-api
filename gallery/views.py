# gallery/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import GalleryImage
from .serializers import GalleryImageSerializer

class GalleryImageView(generics.ListAPIView):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [AllowAny]