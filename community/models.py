# community/models.py

from django.db import models
from django.conf import settings
from films.models import Film

# FIXED: Merged the two Post models into one definitive version.
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
    content = models.TextField() # Standardized on 'content' instead of 'body'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class Comment(models.Model):
    """Comments under posts"""
    user = models.ForeignKey( # FIXED: Field is 'user', not 'author'
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    content = models.TextField() # FIXED: Field is 'content', not 'body'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"


# NEW: Added the Like model which was missing before.
class Like(models.Model):
    """Represents a 'like' on a Post by a User."""
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # REMOVED clashing related_name
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class FilmRating(models.Model):
    """Community-specific film ratings"""
    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        related_name="ratings" # SIMPLIFIED related_name
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    score = models.PositiveIntegerField(default=1) # RENAMED to 'score' for clarity
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("film", "user")

    def __str__(self):
        return f"Rating {self.score} for {self.film} by {self.user.username}"