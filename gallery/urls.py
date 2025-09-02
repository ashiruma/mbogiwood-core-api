# gallery/urls.py
from django.urls import path
from .views import GalleryImageView

app_name = 'gallery'

urlpatterns = [
    path('', GalleryImageView.as_view(), name='gallery-list'),
]