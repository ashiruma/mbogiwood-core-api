from django.db import models
from django.conf import settings
from films.models import Film


class Post(models.Model):
    """Community posts linked to films or general discussions"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        related_name="community_posts",
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} by {self.user}"


class Comment(models.Model):
    """Comments under posts"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"


class FilmRating(models.Model):
    """Community-specific film ratings (kept separate from reviews app)"""
    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        related_name="community_ratings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_film_ratings"
    )
    rating = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("film", "user")

    def __str__(self):
        return f"Rating {self.rating} for {self.film} by {self.user}"
