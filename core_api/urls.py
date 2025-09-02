# core_api/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # API endpoints
    path("api/", include("users.urls")),
    path("api/", include("films.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("analytics.urls")),
    path('api/', include('jobs.urls')),
    path('api/', include('gallery.urls')),
    path('api/', include('about.urls')),
]

# This serves media files (like posters and gallery images) in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)