# about/models.py
from django.db import models

class AboutPageContent(models.Model):
    mission_statement = models.TextField()
    our_story = models.TextField()

    class Meta:
        verbose_name_plural = "About Page Content"

    def __str__(self):
        return "Main About Page Content"

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='team_photos/')
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name