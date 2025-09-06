# community/urls.py

from django.urls import path
# FIXED: Importing the correct view names
from .views import (
    PostListCreateView,
    PostDetailView,
    CommentListCreateView,
    CommentDetailView,
    toggle_like,
    FilmRatingView, # This was renamed
)

urlpatterns = [
    # Post URLs
    path("posts/", PostListCreateView.as_view(), name="post-list-create"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),

    # Comment URLs (nested under posts)
    path("posts/<int:post_pk>/comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),

    # Like URL
    path("posts/<int:post_pk>/like/", toggle_like, name="toggle-like"),

    # Film Rating URL using the new view name
    path("films/<int:film_pk>/ratings/", FilmRatingView.as_view(), name="film-rating"),
]