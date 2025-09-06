# FILE: payments/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from films.models import Film

class Order(models.Model):
    # ... your existing Order model ...

class Payout(models.Model):
    # ... your existing Payout model ...

class PaymentTransaction(models.Model):
    # ... your existing PaymentTransaction model ...

# --- ADD THIS NEW MODEL ---
class PayoutRequest(models.Model):
    """
    Represents a request from a filmmaker to withdraw their earnings.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        PAID = 'paid', 'Paid'

    filmmaker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payout_requests')
    amount_cents = models.PositiveIntegerField()
    mpesa_phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Notes from the admin regarding the request.")

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Payout request of {self.amount_cents / 100} KES for {self.filmmaker.email}"
