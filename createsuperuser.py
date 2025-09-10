import os
import django

# Set up Django
# Make sure 'core_api.settings' matches your project's settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_api.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# --- KEY CHANGES START HERE ---

# Get superuser details from environment variables
# We only need email and password as 'username' does not exist on your User model.
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

# Create a superuser if it doesn't exist
# The condition now checks for 'email' instead of 'username'.
if email and password and not User.objects.filter(email=email).exists():
    print(f"Creating superuser for: {email}")
    
    # The create_superuser method is called with 'email', not 'username'.
    User.objects.create_superuser(email=email, password=password)
    
    print("Superuser created successfully.")
else:
    print("Superuser with this email already exists or environment variables are not set.")