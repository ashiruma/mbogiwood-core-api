# core_api/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Films + Payments
    path("api/films/", include("films.urls", namespace="films")),
    path("api/payments/", include("payments.urls", namespace="payments")),

    # Other apps under /api/
    path("api/users/", include("users.urls")),
    path("api/gallery/", include("gallery.urls")),
    path("api/about/", include("about.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/filmmakers/", include("filmmakers.urls")),
    path("api/community/", include("community.urls")),   # new community app
    path("api/reviews/", include("reviews.urls")),       # reviews app
    path("api/jobs/", include("jobs.urls")),             # jobs app
    path("api/coproduction/", include("coproduction.urls")),
    path("api/news/", include("news.urls")),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
