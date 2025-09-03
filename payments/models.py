# payments/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from films.models import Film


class Order(models.Model):
    # --- Payment Methods ---
    STRIPE = "stripe"
    MPESA = "mpesa"
    PAYMENT_METHOD_CHOICES = [
        (STRIPE, "Stripe"),
        (MPESA, "M-Pesa"),
    ]

    # --- Status ---
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
    ]

    # --- Core fields ---
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default="KES")

    # --- Identifiers ---
    payment_id = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Stripe session ID or M-Pesa CheckoutRequestID"
    )
    transaction_id = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="M-Pesa Transaction ID"
    )
    phone_number = models.CharField(
        max_length=15, blank=True, null=True,
        help_text="Customer phone for M-Pesa"
    )

    # --- Status & Access ---
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    access_expires_at = models.DateTimeField(blank=True, null=True)

    # --- REVENUE TRACKING FIELDS (ADDED) ---
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    filmmaker_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # ----------------------------------------

    def __str__(self):
        return f"Order {self.id} - {self.user.email} - {self.film.title} ({self.status})"

    # --- ACTIVATE ACCESS METHOD (UPDATED) ---
    def activate_access(self):
        """Calculates revenue split, grants rental access, and marks order as successful."""
        # Calculate the 70/30 revenue split
        self.platform_fee = self.amount * Decimal('0.30')
        self.filmmaker_payout = self.amount * Decimal('0.70')
        
        # Set access period and status
        self.status = self.SUCCESS
        self.access_expires_at = timezone.now() + timedelta(days=self.film.rental_period_days)
        self.save()
    # ----------------------------------------

    def has_access(self):
        """Check if user can still watch the film"""
        return (
            self.status == self.SUCCESS
            and self.access_expires_at
            and self.access_expires_at > timezone.now()
        )


class PaymentTransaction(models.Model):
    """Stores raw M-Pesa STK push transaction data"""
    checkout_request_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    result_code = models.IntegerField(blank=True, null=True)
    result_desc = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mpesa_receipt = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.phone_number} - {self.amount} - {self.status}"