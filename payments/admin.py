from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "film", "payment_method", "amount", "currency", "status", "access_expires_at", "created_at")
    list_filter = ("payment_method", "status")
    search_fields = ("user__email", "film__title", "payment_id")
