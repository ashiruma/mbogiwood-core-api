# payments/admin.py
from django.contrib import admin
from .models import Order, Payout, PaymentTransaction, PayoutRequest


# ------------------------
# Inline Models
# ------------------------
class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = (
        "checkout_request_id",
        "merchant_request_id",
        "result_code",
        "result_desc",
        "amount_cents",
        "mpesa_receipt",
        "phone_number",
        "status",
        "created_at",
        "completed_at",
    )
    can_delete = False


# ------------------------
# Order Admin
# ------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "film",
        "payment_method",
        "amount_cents",
        "currency",
        "status",
        "transaction_id",
        "created_at",
        "access_expires_at",
    )
    list_filter = ("status", "payment_method", "currency", "created_at")
    search_fields = ("user__username", "user__email", "film__title", "transaction_id", "payment_id")
    ordering = ("-created_at",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "payment_id",
        "transaction_id",
        "platform_fee_cents",
        "filmmaker_payout_cents",
        "access_expires_at",
    )
    inlines = [PaymentTransactionInline]


# ------------------------
# PaymentTransaction Admin
# ------------------------
@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "checkout_request_id",
        "phone_number",
        "amount_cents",
        "status",
        "mpesa_receipt",
        "result_code",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("checkout_request_id", "mpesa_receipt", "phone_number")
    ordering = ("-created_at",)
    readonly_fields = (
        "checkout_request_id",
        "merchant_request_id",
        "result_code",
        "result_desc",
        "amount_cents",
        "mpesa_receipt",
        "phone_number",
        "status",
        "created_at",
        "completed_at",
    )


# ------------------------
# Payout Admin (Extended for B2C Callbacks)
# ------------------------
@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "filmmaker",
        "amount_cents",
        "status",
        "transaction_id",
        "created_at",
        "completed_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("filmmaker__username", "filmmaker__email", "transaction_id")
    readonly_fields = ("created_at", "completed_at")

    fieldsets = (
        ("Payout Info", {
            "fields": ("filmmaker", "amount_cents", "status", "transaction_id")
        }),
        ("Timestamps", {
            "fields": ("created_at", "completed_at")
        }),
        ("M-Pesa B2C Callback", {
            "fields": (
                "result_code",
                "result_desc",
                "mpesa_receipt",
                "b2c_utility_account",
                "b2c_working_account",
                "b2c_charges_paid_account",
            ),
        }),
    )


# ------------------------
# PayoutRequest Admin
# ------------------------
@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "filmmaker",
        "amount_cents",
        "mpesa_phone_number",
        "status",
        "requested_at",
        "reviewed_at",
    )
    list_filter = ("status", "requested_at")
    search_fields = ("filmmaker__username", "filmmaker__email", "mpesa_phone_number")
    readonly_fields = ("requested_at",)
