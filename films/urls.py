# films/urls.py
from django.urls import path
from .views import (
    film_list_api,
    film_detail_api,
    FilmUploadView,
    FilmmakerFilmListView,
    dev_dashboard
)

app_name = 'films'

urlpatterns = [
    path('dashboard/my-films/', FilmmakerFilmListView.as_view(), name='filmmaker-film-list'),
    path('upload/', FilmUploadView.as_view(), name='film-upload'),
    path('<slug:slug>/', film_detail_api, name='film-detail'),
    path('', film_list_api, name='film-list'),
    path('dashboard/', dev_dashboard, name='dev_dashboard'),
]