from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # API routes
    path("api/films/", include(("films.urls", "films"), namespace="films")),
    path("api/payments/", include(("payments.urls", "payments"), namespace="payments")),
    path("api/users/", include("users.urls")),
    path("api/gallery/", include("gallery.urls")),
    path("api/about/", include("about.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/filmmakers/", include("filmmakers.urls")),
    path("api/community/", include("community.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/jobs/", include("jobs.urls")),
    path("api/coproduction/", include("coproduction.urls")),
    path("api/news/", include("news.urls")),
]

# Serve media files in development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
