# about/models.py
from django.db import models

class AboutPageContent(models.Model):
    mission_statement = models.TextField(blank=True)
    vision_statement = models.TextField(blank=True)
    our_story = models.TextField(blank=True)
    our_values = models.TextField(blank=True)

    # --- ADD THESE FIELDS ---
    films_featured = models.PositiveIntegerField(default=500)
    professionals_connected = models.CharField(max_length=20, default="10K")
    countries_reached = models.PositiveIntegerField(default=50)
    hours_watched = models.CharField(max_length=20, default="1M")
    # ------------------------

    class Meta:
        verbose_name_plural = "About Page Content"

    def __str__(self):
        return "Main About Page Content"

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team_photos/')
    bio = models.TextField(blank=True, null=True)  # <-- Add this line
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name