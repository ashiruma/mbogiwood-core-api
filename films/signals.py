# films/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Film
from .tasks import convert_film_to_hls

@receiver(post_save, sender=Film)
def trigger_hls_conversion(sender, instance, created, **kwargs):
    # 'created' is True only the first time the object is saved
    if created and instance.video_file:
        convert_film_to_hls.delay(instance.id)