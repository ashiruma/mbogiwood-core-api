# films/models.py
from django.db import models
from django.utils.text import slugify
from django.conf import settings

class Category(models.Model):
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
    STATUS_CHOICES = [(PROMO, "Promo"), (PAID, "Paid")]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    # --- FIELD ADDED HERE ---
    release_date = models.DateField(null=True, blank=True)
    # ------------------------
    
    poster = models.ImageField(upload_to="films/posters/", blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to="films/videos/", blank=True, null=True)

    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    rental_period_days = models.PositiveIntegerField(default=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PAID)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="films")
    filmmaker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='films',
        null=True
    )

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