# users/urls.py
from django.urls import path, include

# app_name is not needed when using djoser this way
# app_name = "users"

urlpatterns = [
    # This includes the token-based authentication endpoints:
    # POST /api/auth/token/login/ - for logging in
    # POST /api/auth/token/logout/ - for logging out
    path('auth/', include('djoser.urls.authtoken')),

    # This includes all the main Djoser user endpoints like:
    # POST /api/users/ - for creating users (registration)
    # GET /api/users/me/ - for getting the current user's details
    # ... and others
    path('', include('djoser.urls')),
]