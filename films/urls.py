# ===================================================================
# --- IMPORTS ---
# ===================================================================
from django.urls import path, include
from .views import (
    # Public API Views
    film_list_api,
    film_detail_api,

    # Filmmaker-Specific API Views
    FilmUploadView,
    FilmmakerFilmListView,
    FilmStreamView,
    filmmaker_revenue_api,
)

app_name = "films"

# ===================================================================
# --- URL PATTERNS ---
# ===================================================================
urlpatterns = [
    # --- API Endpoints for Frontend (DRF) ---

    # Public-facing endpoints for all users
    path("api/", film_list_api, name="film-list-api"),
    path("api/<slug:slug>/", film_detail_api, name="film-detail-api"),

    # Filmmaker-specific endpoints (protected)
    path("api/upload/", FilmUploadView.as_view(), name="film-upload-api"),
    path("api/dashboard/my-films/", FilmmakerFilmListView.as_view(), name="filmmaker-film-list-api"),
    path("api/filmmaker/revenue/", filmmaker_revenue_api, name="filmmaker-revenue-api"),
    path("api/<int:pk>/stream/", FilmStreamView.as_view(), name="film-stream-api"),

    # --- Nested App URLs (Reviews/Community) ---
    path("api/<slug:slug>/reviews/", include("reviews.urls")),
]
