# gallery/admin.py
from django.contrib import admin
from .models import GalleryImage

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """
    Configuration for the GalleryImage model in the admin panel.
    """
    list_display = ('title', 'uploaded_at')
    search_fields = ('title', 'description')
    list_filter = ('uploaded_at',)