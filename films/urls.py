from rest_framework.routers import DefaultRouter
from .views import FilmViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'films', FilmViewSet, basename="films")
router.register(r'categories', CategoryViewSet, basename="categories")

urlpatterns = router.urls

app_name = "films"
