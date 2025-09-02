# filmmakers/urls.py
from django.urls import path
from .views import ApplicationCreateView

app_name = 'filmmakers'

urlpatterns = [
    path('apply/', ApplicationCreateView.as_view(), name='filmmaker-apply'),
]