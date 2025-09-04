# filmmakers/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class FilmmakerApplication(models.Model):
    """ Stores an application from a user wanting to become a filmmaker. """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="filmmaker_application")
    reasons = models.TextField(help_text="Why do you want to join Mbogiwood?")
    previous_works_links = models.TextField(blank=True, help_text="Links to your previous films.")
    showreel_link = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Application for {self.user.email} ({self.status})"

    def approve(self):
        # Assumes your CustomUser model has a 'role' field
        self.user.role = 'filmmaker' 
        self.user.save()
        self.status = self.Status.APPROVED
        self.reviewed_at = timezone.now()
        self.save()

    def reject(self):
        self.status = self.Status.REJECTED
        self.reviewed_at = timezone.now()
        self.save()