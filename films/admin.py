# films/admin.py
from django.contrib import admin
from .models import Film, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Configuration for the Category model in the admin panel.
    """
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} # Automatically creates a slug from the name

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    """
    Configuration for the Film model in the admin panel.
    """
    # 1. Customize the columns shown in the list of films
    list_display = ('id', 'title', 'status', 'category', 'created_at')
    
    # 2. Add a filter sidebar
    list_filter = ('status', 'category')
    
    # 3. Add a search bar
    search_fields = ('title', 'description')
    
    # Automatically create the slug from the title
    prepopulated_fields = {'slug': ('title',)}
    
    # Organize the fields in the add/edit form
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'poster', 'category')
        }),
        ('Status & Pricing', {
            'fields': ('status', 'price')
        }),
        ('Video Content', {
            'fields': ('trailer_url', 'video_file')
        }),
    )
    
    # Show read-only date fields
    readonly_fields = ('created_at', 'updated_at')