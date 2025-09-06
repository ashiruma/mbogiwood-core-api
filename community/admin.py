# FILE: community/admin.py

from django.contrib import admin
from .models import Post, Comment, Like, FilmRating

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "film", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "content", "user__username")
    ordering = ("-created_at",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content", "user__username", "post__title")
    ordering = ("-created_at",)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
    search_fields = ("user__username", "post__title")

@admin.register(FilmRating)
class FilmRatingAdmin(admin.ModelAdmin):
    list_display = ("film", "user", "score", "created_at")
    list_filter = ("score", "created_at")
    search_fields = ("film__title", "user__username")
    ordering = ("-created_at",)