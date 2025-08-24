from django.contrib import admin
from .models import Film

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "price", "rental_period_days", "created_at")
    list_filter = ("status",)
    search_fields = ("title",)
