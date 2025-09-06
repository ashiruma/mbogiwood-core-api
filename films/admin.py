# films/admin.py
from django.contrib import admin
from .models import Film, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "price",
        "rental_period_days",
        "processing_status",
        "created_at",
    )
    list_filter = ("status", "processing_status", "category")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
