# payments/admin.py
from django.contrib import admin
from .models import Order, PaymentTransaction


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "film", "payment_method",
        "amount", "currency", "status", "created_at", "access_expires_at"
    )
    list_filter = ("payment_method", "status", "currency", "created_at")
    search_fields = ("user__email", "film__title", "payment_id", "transaction_id")
    readonly_fields = ("created_at", "updated_at", "access_expires_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Order Info", {
            "fields": ("user", "film", "payment_method", "amount", "currency")
        }),
        ("Identifiers", {
            "fields": ("payment_id", "transaction_id", "phone_number")
        }),
        ("Status & Access", {
            "fields": ("status", "access_expires_at")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "phone_number", "amount", "status",
        "checkout_request_id", "mpesa_receipt", "created_at", "completed_at"
    )
    list_filter = ("status", "created_at")
    search_fields = ("phone_number", "checkout_request_id", "mpesa_receipt")
    readonly_fields = ("created_at", "completed_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Transaction Info", {
            "fields": ("checkout_request_id", "merchant_request_id", "mpesa_receipt")
        }),
        ("Payment Data", {
            "fields": ("amount", "phone_number", "status", "result_code", "result_desc")
        }),
        ("Timestamps", {
            "fields": ("created_at", "completed_at"),
        }),
    )
