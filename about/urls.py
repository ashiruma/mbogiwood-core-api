# about/urls.py
from django.urls import path
from .views import AboutPageView

app_name = 'about'

urlpatterns = [
    # This now correctly creates the URL /api/about/
    path('', AboutPageView.as_view(), name='about-content'),
]