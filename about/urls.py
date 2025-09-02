# about/urls.py
from django.urls import path
from .views import AboutPageView

app_name = 'about'

urlpatterns = [
    path('', AboutPageView.as_view(), name='about-content'),
]