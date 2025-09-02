# gallery/urls.py
from django.urls import path
from .views import GalleryImageView

app_name = 'gallery'

urlpatterns = [
    # This now correctly creates the URL /api/gallery/
    path('', GalleryImageView.as_view(), name='gallery-list'),
]