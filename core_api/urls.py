# ===================================================================
# --- IMPORTS ---
# ===================================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ===================================================================
# --- URL PATTERNS ---
# ===================================================================
urlpatterns = [
    path("admin/", admin.site.urls),

    # Films app
    path("films/", include("films.urls", namespace="films")),

    # Payments app
    path("payments/", include("payments.urls", namespace="payments")),

    # Other apps
    path("api/users/", include("users.urls")),
    path("api/gallery/", include("gallery.urls")),
    path("api/about/", include("about.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/filmmakers/", include("filmmakers.urls")),
]

# Media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
