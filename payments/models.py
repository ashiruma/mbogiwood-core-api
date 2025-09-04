# payments/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from films.models import Film

class Order(models.Model):
    """
    Represents a complete purchase order for a film by a user.
    This is the primary model for tracking a transaction's status and revenue.
    """
    # --- Choices for fields ---
    class PaymentMethod(models.TextChoices):
        STRIPE = 'stripe', 'Stripe'
        MPESA = 'mpesa', 'M-Pesa'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    # --- Core fields ---
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="orders")
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    amount_cents = models.PositiveIntegerField(help_text="Total amount paid in KES cents")
    currency = models.CharField(max_length=10, default="KES")

    # --- Payment Gateway Identifiers ---
    payment_id = models.CharField(max_length=255, blank=True, null=True, help_text="Stripe session ID or M-Pesa CheckoutRequestID")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="Final M-Pesa Transaction ID")
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Customer phone for M-Pesa")

    # --- Status, Access & Revenue ---
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    access_expires_at = models.DateTimeField(blank=True, null=True)
    platform_fee_cents = models.PositiveIntegerField(default=0)
    filmmaker_payout_cents = models.PositiveIntegerField(default=0)
    
    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} for '{self.film.title}' by {self.user.email} ({self.status})"

    def activate_access(self):
        """Calculates revenue split, grants rental access, and marks order as successful."""
        if self.status == self.SUCCESS:
            return # Prevent running this logic twice

        # Calculate the 70/30 revenue split using integers
        self.platform_fee_cents = int(self.amount_cents * 0.30)
        self.filmmaker_payout_cents = self.amount_cents - self.platform_fee_cents
        
        # Set access period and status
        self.status = self.Status.SUCCESS
        self.access_expires_at = timezone.now() + timedelta(days=self.film.rental_period_days)
        self.save()

    def has_access(self):
        """Check if the user can still watch the film."""
        return self.status == self.Status.SUCCESS and self.access_expires_at and self.access_expires_at > timezone.now()


class Payout(models.Model):
    """ Records a payout transaction made to a filmmaker. """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    filmmaker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payouts')
    amount_cents = models.PositiveIntegerField(help_text="Payout amount in KES cents")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="M-Pesa Transaction ID for the payout.")

    def __str__(self):
        return f"Payout of {self.amount_cents / 100} KES to {self.filmmaker.email}"

class PaymentTransaction(models.Model):
    """
    Stores the raw, unprocessed data from an M-Pesa STK push callback.
    This acts as a log and is used to update the status of an Order.
    """
    checkout_request_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    result_code = models.IntegerField(blank=True, null=True)
    result_desc = models.TextField(blank=True, null=True)
    amount_cents = models.PositiveIntegerField(blank=True, null=True, help_text="Amount in KES cents")
    mpesa_receipt = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.phone_number} - {self.checkout_request_id} - {self.status}"