# filmmakers/admin.py
from django.contrib import admin
from .models import FilmmakerApplication

@admin.register(FilmmakerApplication)
class FilmmakerApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'bio')
    actions = ['approve_applications']

    def approve_applications(self, request, queryset):
        for application in queryset:
            user = application.user
            user.role = 'filmmaker' # Assumes 'filmmaker' is a valid choice in your CustomUser model
            user.save()
            application.status = FilmmakerApplication.Status.APPROVED
            application.save()
    approve_applications.short_description = "Approve selected applications and upgrade user role"