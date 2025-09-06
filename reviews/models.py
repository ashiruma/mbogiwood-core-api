from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from films.models import Film



class Review(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("film", "user")  # user can only review a film once

    def __str__(self):
        return f"Review for {self.film.title} by {self.user.email}"


class Rating(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="review_ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    value = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("film", "user")  # one rating per user per film
        ordering = ["-created_at"]

    def __str__(self):
        return f"Rating {self.value} for {self.film.title} by {self.user.email}"
   
