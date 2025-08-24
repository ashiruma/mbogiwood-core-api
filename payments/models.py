# payments/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from films.models import Film


class Order(models.Model):
    STRIPE = "stripe"
    MPESA = "mpesa"
    PAYMENT_METHOD_CHOICES = [
        (STRIPE, "Stripe"),
        (MPESA, "M-Pesa"),
    ]

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="orders")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_id = models.CharField(max_length=255, blank=True, null=True)  # Stripe session ID / M-Pesa checkout request ID
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default="KES")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Access control
    access_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.email} - {self.film.title} ({self.status})"

    def activate_access(self):
        """Grant rental access when payment succeeds"""
        self.status = self.SUCCESS
        self.access_expires_at = timezone.now() + timedelta(days=self.film.rental_period_days)
        self.save()

    def has_access(self):
        """Check if user can still watch the film"""
        return self.status == self.SUCCESS and self.access_expires_at and self.access_expires_at > timezone.now()


