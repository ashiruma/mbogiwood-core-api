# films/urls.py

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
    filmmaker_revenue_api, # Renamed to match the view function in views.py

    # NOTE: Add your template-rendering and payment views here if needed
    # create_checkout_session,
    # payment_success,
    # payment_cancel,
    # watch_film,
)

app_name = 'films'

# ===================================================================
# --- URL PATTERNS ---
# ===================================================================

urlpatterns = [
    # --- API Endpoints for Frontend (DRF) ---

    # Public-facing endpoints for all users
    path('api/', film_list_api, name='film-list-api'),
    path('api/<slug:slug>/', film_detail_api, name='film-detail-api'),

    # Filmmaker-specific endpoints (protected)
    path('api/upload/', FilmUploadView.as_view(), name='film-upload-api'),
    path('api/dashboard/my-films/', FilmmakerFilmListView.as_view(), name='filmmaker-film-list-api'),
    path('api/filmmaker/revenue/', filmmaker_revenue_api, name='filmmaker-revenue-api'),
    path('api/<int:pk>/stream/', FilmStreamView.as_view(), name="film-stream-api"),

    # --- Nested App URLs ---
    # Includes all URLs from the 'reviews' app, nested under a specific film
    path('api/<slug:slug>/reviews/', include('reviews.urls')),

    # --- Template Rendering & Payment URLs (Standard Django) ---
    # This is where you would place URLs that render HTML pages or handle form posts.
    # Example:
    # path('watch/<slug:slug>/', watch_film, name='watch-film'),
    # path('payment/create-session/<slug:slug>/', create_checkout_session, name='create-checkout-session'),
    # path('payment/success/', payment_success, name='payment-success'),
    # path('payment/cancel/', payment_cancel, name='payment-cancel'),
]