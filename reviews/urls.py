# reviews/urls.py
from django.urls import path
from .views import ReviewListView, ReviewCreateView

app_name = 'reviews'

urlpatterns = [
    # Creates URLs like: /api/films/<slug>/reviews/
    path('', ReviewListView.as_view(), name='review-list'),
    path('create/', ReviewCreateView.as_view(), name='review-create'),
]