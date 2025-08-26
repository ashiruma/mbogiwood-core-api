# films/admin.py
from django.contrib import admin
from .models import Category, Film


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "price", "rental_period_days", "category", "created_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "slug", "description", "status", "category")
        }),
        ("Media", {
            "fields": ("poster", "trailer_url", "video_file")
        }),
        ("Business", {
            "fields": ("price", "rental_period_days")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )
