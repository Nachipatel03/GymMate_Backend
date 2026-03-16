import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymMate.settings')
django.setup()

from accounts.models import CustomUser

def create_admin():
    email = "nachipatel0322@gmail.com"
    password = "@NIck0314"
    username = "nachipatel"  # Required field
    
    if not CustomUser.objects.filter(email=email).exists():
        CustomUser.objects.create_superuser(
            email=email,
            username=username,
            password=password,
            role="ADMIN"
        )
        print(f"Admin user {email} created successfully.")
    else:
        print(f"User {email} already exists.")

if __name__ == "__main__":
    create_admin()
