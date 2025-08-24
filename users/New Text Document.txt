# users/utils.py

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    verification_path = reverse('user_verify_email', kwargs={'uidb64': uid, 'token': token})
    verification_url = request.build_absolute_uri(verification_path)
    
    subject = "Verify Your Mbogiwood Account"
    message = f"""
    Hi {user.full_name},

    Thank you for registering at Mbogiwood. Please click the link below to verify your email address:
    {verification_url}

    If you did not create an account, please ignore this email.

    Thanks,
    The Mbogiwood Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_from_email,
        [user.email],
        fail_silently=False,
    )