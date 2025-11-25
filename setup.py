#!/usr/bin/env python
"""
Setup script for FineBooks Django project
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_project():
    """Setup the project with migrations and superuser creation"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finebooks.settings')
    django.setup()
    
    # Run migrations
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create superuser if it doesn't exist
    print("Creating superuser...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@email.com', 'admin123')
            print("Superuser created: admin/admin123")
        else:
            print("Superuser already exists")
    except Exception as e:
        print(f"Error creating superuser: {e}")
    
    print("Setup complete! Run 'python manage.py runserver' to start the server.")

if __name__ == '__main__':
    setup_project() 