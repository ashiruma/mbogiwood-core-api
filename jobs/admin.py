from django.contrib import admin
from .models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "status", "deadline", "posted_by", "created_at")
    list_filter = ("status", "company", "deadline")
    search_fields = ("title", "company", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("job__title", "applicant__email", "cover_letter")
    autocomplete_fields = ("job", "applicant")
    ordering = ("-created_at",)
