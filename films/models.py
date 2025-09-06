from django.db import models
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    """Represents a film category (e.g., Action, Drama, Comedy)."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        """Auto-generate a unique slug if not set."""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Film(models.Model):
    """Represents a single film available on the platform."""

    # --- Status ---
    PROMO = "promo"
    PAID = "paid"
    STATUS_CHOICES = [(PROMO, "Promo"), (PAID, "Paid")]

    class ProcessingStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    # --- Core Info ---
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    poster = models.ImageField(upload_to="films/posters/", blank=True, null=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="films",
    )
    filmmaker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="films",
        null=True,  # allows admin uploads without a filmmaker
    )

    # --- Video & Streaming ---
    trailer_url = models.URLField(blank=True, null=True)
    trailer_file = models.FileField(upload_to="films/trailers/", blank=True, null=True)
    video_file = models.FileField(upload_to="films/videos/", blank=True, null=True)
    hls_manifest = models.FileField(upload_to="films/hls/", blank=True, null=True)

    # --- Monetization ---
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PAID)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rental_period_days = models.PositiveIntegerField(default=2)

    # --- Processing ---
    processing_status = models.CharField(
        max_length=10,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
    )
    processing_log = models.TextField(blank=True, null=True)

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        """Auto-generate a unique slug from title if not set."""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Film.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    # --- Helpers ---
    @property
    def price_kes(self):
        """Return price as integer in KES (drop cents)."""
        return int(self.price)

    @property
    def hls_manifest_path(self):
        """Compatibility property for streaming views."""
        return self.hls_manifest.url if self.hls_manifest else None

    def __str__(self):
        return self.title
