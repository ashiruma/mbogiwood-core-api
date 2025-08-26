from django.urls import path
from . import views

urlpatterns = [
    path("ping/", views.ping, name="users-ping"),
    path("", views.UserListView.as_view(), name="user-list"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
]
