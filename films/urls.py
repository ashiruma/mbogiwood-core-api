# films/urls.py
from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import FilmViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'films', FilmViewSet, basename="films")
router.register(r'categories', CategoryViewSet, basename="categories")

urlpatterns = router.urls

app_name = "films"

urlpatterns = [
    path("", views.ping, name="films-root"),  # root endpoint for /api/films/
    path("ping/", views.ping, name="films-ping"),
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("categories/<slug:slug>/", views.CategoryDetailView.as_view(), name="category-detail"),
    path("list/", views.FilmListView.as_view(), name="film-list"),
    path("<slug:slug>/", views.FilmDetailView.as_view(), name="film-detail"),
]
