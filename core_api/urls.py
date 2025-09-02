# core_api/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def home(request):
    return JsonResponse({"status": "ok", "message": "Welcome to the Mbogiwood Core API"})

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),

    # Defines the base URL for each app
    path("api/users/", include("users.urls")),
    path("api/films/", include("films.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/jobs/", include("jobs.urls")),
    path("api/gallery/", include("gallery.urls")),
    path("api/about/", include("about.urls")),
    path("api/filmmakers/", include("filmmakers.urls")),
    path("api/analytics/", include("analytics.urls")),
]

# This correctly serves your uploaded media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)