from django.contrib import admin
from django.urls import path, include

urlpatterns = [
   
    # API endpoints
    path("api/users/", include("users.urls")),
    path("api/films/", include("films.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("payments/", include("payments.urls")),
]
