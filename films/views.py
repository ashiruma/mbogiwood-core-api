from rest_framework import viewsets
from .models import Film, Category
from .serializers import FilmSerializer, CategorySerializer


class FilmViewSet(viewsets.ModelViewSet):
    queryset = Film.objects.all().order_by("-created_at")
    serializer_class = FilmSerializer
    lookup_field = "slug"   # so you can use /api/films/<slug>/


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    lookup_field = "slug"
