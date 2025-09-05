from django.urls import path
from .views import (
    ReviewListCreateView,
    ReviewDetailView,
    RatingListCreateView,
    RatingDetailView,
)

app_name = "reviews"

urlpatterns = [
    # Reviews
    path("<slug:film_slug>/reviews/", ReviewListCreateView.as_view(), name="review-list-create"),
    path("reviews/<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),

    # Ratings
    path("<slug:film_slug>/ratings/", RatingListCreateView.as_view(), name="rating-list-create"),
    path("ratings/<int:pk>/", RatingDetailView.as_view(), name="rating-detail"),
]
