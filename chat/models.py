# community/models.py
from django.conf import settings
from django.db import models
from films.models import Film


class Category(models.TextChoices):
    GENERAL = "general", "General"
    FILMS = "films", "Films"
    CULTURE = "culture", "Culture"
    EVENTS = "events", "Events"


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_posts")
    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.GENERAL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.user})"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user} likes {self.post}"


# --- Film Ratings ---
class FilmRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="film_ratings")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveSmallIntegerField()  # 1 to 5 stars
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "film")  # One rating per user per film

    def __str__(self):
        return f"{self.user} rated {self.film} {self.rating}★"
