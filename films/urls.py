# films/urls.py
from django.urls import path
from .views import (
    film_list_api, 
    film_detail_api, 
    FilmUploadView,
    FilmmakerFilmListView
)

app_name = 'films'

urlpatterns = [
    # Most specific paths first
    path('dashboard/my-films/', FilmmakerFilmListView.as_view(), name='filmmaker-film-list'),
    path('upload/', FilmUploadView.as_view(), name='film-upload'),
    
    # General slug-based path
    path('<slug:slug>/', film_detail_api, name='film-detail'),
    
    # Root path for the app, matched last
    path('', film_list_api, name='film-list'),
]