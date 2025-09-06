from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from films.models import Film


class Order(models.Model):
    """Represents a purchase order for a film."""

    class PaymentMethod(models.TextChoices):
        STRIPE = "stripe", "Stripe"
        MPESA = "mpesa", "M-Pesa"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    amount_cents = models.PositiveIntegerField(help_text="Total amount paid in cents (KES*100).")
    currency = models.CharField(max_length=10, default="KES")

    payment_id = models.CharField(max_length=255, blank=True, null=True)  # Stripe session / M-Pesa CheckoutRequestID
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # Final M-Pesa Receipt
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    access_expires_at = models.DateTimeField(blank=True, null=True)
    platform_fee_cents = models.PositiveIntegerField(default=0)
    filmmaker_payout_cents = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} | {self.film.title} | {self.user.email} | {self.status}"

    def activate_access(self):
        """Mark order as successful and grant film access."""
        if self.status == self.Status.SUCCESS:
            return
        self.platform_fee_cents = int(self.amount_cents * 0.30)
        self.filmmaker_payout_cents = self.amount_cents - self.platform_fee_cents
        self.status = self.Status.SUCCESS
        self.access_expires_at = timezone.now() + timedelta(days=self.film.rental_period_days)
        self.save()

    def has_access(self):
        return (
            self.status == self.Status.SUCCESS
            and self.access_expires_at
            and self.access_expires_at > timezone.now()
        )


class Payout(models.Model):
    """Tracks payouts to filmmakers."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    filmmaker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payouts",
    )
    amount_cents = models.PositiveIntegerField(help_text="Payout amount in cents (KES*100).")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payout {self.id} | {self.amount_cents / 100:.2f} KES | {self.filmmaker.email}"


class PaymentTransaction(models.Model):
    """Raw M-Pesa callback data (acts as a log)."""

    checkout_request_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    result_code = models.IntegerField(blank=True, null=True)
    result_desc = models.TextField(blank=True, null=True)
    amount_cents = models.PositiveIntegerField(blank=True, null=True, help_text="Amount in cents (KES*100).")
    mpesa_receipt = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, default="PENDING")

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Txn {self.checkout_request_id} | {self.phone_number} | {self.status}"
