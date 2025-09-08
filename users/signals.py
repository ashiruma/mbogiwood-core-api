# FILE: users/signals.py

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CustomUser # Or your user model

@receiver(post_save, sender=CustomUser)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Sends a welcome email when a new user is created.
    """
    if created:
        send_mail(
            'Welcome to Mbogiwood Productions!',
            f'Hi {instance.first_name},\n\nThank you for joining our community. We are excited to have you on board.',
            settings.EMAIL_HOST_USER,
            [instance.email],
            fail_silently=False,
        )