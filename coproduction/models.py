# FILE: coproduction/models.py

from django.db import models
from django.conf import settings

class Project(models.Model):
    """
    Represents a film project idea posted by a filmmaker.
    """
    class Status(models.TextChoices):
        IDEA = 'idea', 'Idea'
        IN_DEVELOPMENT = 'in_development', 'In Development'
        IN_PRODUCTION = 'in_production', 'In Production'
        COMPLETED = 'completed', 'Completed'

    title = models.CharField(max_length=255)
    logline = models.CharField(max_length=500, help_text="A short, one-sentence summary of the project.")
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IDEA)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    roles_needed = models.CharField(max_length=500, help_text="Comma-separated list of roles needed (e.g., Director, Cinematographer).")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CollaborationProposal(models.Model):
    """
    Represents a proposal from one user to collaborate on another user's project.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    proposer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proposals')
    message = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal from {self.proposer.email} for {self.project.title}"