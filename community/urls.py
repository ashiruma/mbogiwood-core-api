# community/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.PostListCreateView.as_view(), name="post-list"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("comments/", views.CommentCreateView.as_view(), name="comment-create"),
    path("posts/<int:post_id>/toggle-like/", views.ToggleLikeView.as_view(), name="toggle-like"),
    path("films/<int:film_id>/rate/", views.FilmRatingView.as_view(), name="film-rate"),
    path("films/<int:id>/ratings/", views.FilmWithRatingsView.as_view(), name="film-ratings"),
]
