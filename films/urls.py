# FILE: films/urls.py
from django.urls import path, include
from .views import (
    film_list_api,
    film_detail_api,
    FilmUploadView,
    FilmmakerFilmListView,
    filmmaker_revenue_api,
    SecureFilmStreamView,
)

app_name = "films"

urlpatterns = [
    # Public API Endpoints
    path("", film_list_api, name="film-list-api"),
    path("<slug:slug>/", film_detail_api, name="film-detail-api"),

    # Filmmaker Endpoints
    path("upload/", FilmUploadView.as_view(), name="film-upload-api"),
    path("dashboard/my-films/", FilmmakerFilmListView.as_view(), name="filmmaker-film-list-api"),
    path("filmmaker/revenue/", filmmaker_revenue_api, name="filmmaker-revenue-api"),

    # Streaming - Use a single, clean URL
    path("<int:pk>/stream/", SecureFilmStreamView.as_view(), name="film-stream-api"),

    # Nested App URLs
    path("<slug:slug>/reviews/", include("reviews.urls")),
]