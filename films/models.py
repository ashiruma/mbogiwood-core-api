# films/models.py
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Optional categories for organizing films"""
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
    PROMO = "promo"
    PAID = "paid"
    STATUS_CHOICES = [
        (PROMO, "Promo"),
        (PAID, "Paid"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    # Media
    poster = models.ImageField(upload_to="films/posters/", blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)  # optional trailer
    video_file = models.FileField(upload_to="films/videos/", blank=True, null=True)  # or S3 path

    # Business logic
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    rental_period_days = models.PositiveIntegerField(default=2)  # default 2-day access
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PAID)

    # Relationships
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="films")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
