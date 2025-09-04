from django.conf import settings
from django.db import models
from django.utils import timezone


class Payout(models.Model):
METHOD_CHOICES = (
("MPESA", "M-Pesa"),
("STRIPE", "Stripe"),
)
filmmaker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payouts")
amount_cents = models.PositiveIntegerField()
method = models.CharField(max_length=10, choices=METHOD_CHOICES)
status = models.CharField(max_length=20, default="PENDING") # PENDING, APPROVED, PAID, FAILED
requested_at = models.DateTimeField(default=timezone.now)
processed_at = models.DateTimeField(null=True, blank=True)
reference = models.CharField(max_length=128, blank=True, default="")


class Meta:
ordering = ["-requested_at"]