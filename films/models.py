# films/models.py
from django.db import models
from django.utils.text import slugify
from django.conf import settings

class Category(models.Model):
    """Represents a film category, like 'Action', 'Drama', etc."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Film(models.Model):
    """Represents a single film available on the platform."""
    # --- Status Choices ---
    PROMO = "promo"
    PAID = "paid"
    STATUS_CHOICES = [(PROMO, "Promo"), (PAID, "Paid")]

    # --- Core Information ---
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    poster = models.ImageField(upload_to="films/posters/", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="films")
    filmmaker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='films',
        null=True # Can be null if uploaded by an admin
    )

    # --- Video & Streaming ---
    trailer_url = models.URLField(blank=True, null=True, help_text="Link to the trailer on YouTube, Vimeo, etc.")
    video_file = models.FileField(upload_to="films/videos/", blank=True, null=True, help_text="The original high-quality video file.")
    hls_manifest_path = models.CharField(max_length=512, blank=True, default="", help_text="Path to the HLS .m3u8 manifest file.")

    # --- Monetization ---
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PAID)
    price_cents = models.PositiveIntegerField(default=0, help_text="Price in KES cents (e.g., 50000 for KES 500.00)")
    rental_period_days = models.PositiveIntegerField(default=2)

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Auto-generate slug from the title if it's not provided
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title