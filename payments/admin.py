# payments/admin.py
from django.contrib import admin
from .models import Order, PaymentTransaction, Payout

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "film",
        "status",
        "display_amount", # Use the custom method here
        "created_at",
    )
    list_filter = ("payment_method", "status", "created_at")
    search_fields = ("user__email", "film__title", "payment_id")
    readonly_fields = (
        "created_at",
        "updated_at",
        "access_expires_at",
        "platform_fee_cents",
        "filmmaker_payout_cents",
    )
    ordering = ("-created_at",)

    fieldsets = (
        ("Order Info", {
            "fields": ("user", "film", "payment_method", "amount_cents", "currency")
        }),
        ("Revenue Split", {
            "fields": ("platform_fee_cents", "filmmaker_payout_cents")
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

    @admin.display(description='Amount (KES)')
    def display_amount(self, obj):
        """Formats the cents value into a readable KES string."""
        return f"{obj.amount_cents / 100:.2f}"


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "phone_number",
        "display_amount", # Use the custom method here
        "status",
        "checkout_request_id",
        "created_at",
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
            "fields": ("amount_cents", "phone_number", "status", "result_code", "result_desc")
        }),
        ("Timestamps", {
            "fields": ("created_at", "completed_at"),
        }),
    )

    @admin.display(description='Amount (KES)')
    def display_amount(self, obj):
        """Formats the cents value into a readable KES string."""
        if obj.amount_cents is not None:
            return f"{obj.amount_cents / 100:.2f}"
        return "N/A"


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "filmmaker",
        "status",
        "display_amount", # Use the custom method here
        "created_at",
        "transaction_id"
    )
    list_filter = ("status",)
    search_fields = ("filmmaker__email", "transaction_id")
    readonly_fields = ("created_at", "completed_at")
    ordering = ("-created_at",)

    @admin.display(description='Amount (KES)')
    def display_amount(self, obj):
        """Formats the cents value into a readable KES string."""
        return f"{obj.amount_cents / 100:.2f}"