from django.urls import path, include
from .views import UserListView, UserDetailView

urlpatterns = [
    # --- Custom User Endpoints ---
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),

    # --- Auth / Djoser Integration ---
    path("auth/", include("djoser.urls.authtoken")),
    path("", include("djoser.urls")),
]
