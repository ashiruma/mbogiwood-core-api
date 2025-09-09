# users/admin.py (Updated Version)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuration for the CustomUser model in the Django admin.
    Integrates all custom fields for easy management.
    """
    # Fields to display in the main list view of users
    list_display = ('email', 'full_name', 'role', 'is_staff', 'is_active', 'date_joined')
    
    # Fields that can be used to filter the user list
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')
    
    # Fields that can be searched
    search_fields = ('email', 'full_name')
    
    # Default ordering to show newest users first
    ordering = ('-date_joined',)
    
    # The fields to display on the user EDITING form.
    # We group them into logical sections.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'mpesa_payout_number')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_email_verified', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # The fields to display on the user CREATION form.
    # 'password2' is for the confirmation field.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password', 'password2'),
        }),
    )