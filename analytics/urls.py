# analytics/urls.py
from django.urls import path
from .views import FilmmakerEarningsView

app_name = 'analytics'

urlpatterns = [
    # Creates the URL /api/analytics/earnings/
    path('earnings/', FilmmakerEarningsView.as_view(), name='filmmaker-earnings'),
]