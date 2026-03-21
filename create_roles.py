#!/usr/bin/env python3
"""
Create Default Roles Script for PlantNest
This script creates default roles for the application.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_store.settings')
django.setup()

from apps.user_management.models import Role

def create_default_roles():
    """Create default roles for the application"""
    
    roles_data = [
        {
            'name': 'Admin',
            'description': 'Administrative access to manage store operations'
        },
        {
            'name': 'Customer',
            'description': 'Regular customer with standard shopping permissions'
        }
    ]
    
    print("Creating default roles...")
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={
                'description': role_data['description']
            }
        )
        
        if created:
            print(f"✓ Created role: {role_data['name']}")
        else:
            print(f"✓ Role already exists: {role_data['name']}")
    
    print("\n🎯 Default roles created successfully!")
    print("\nAvailable roles:")
    for role in Role.objects.all():
        print(f"- {role.name}: {role.description}")
    
    print("\nNext steps:")
    print("1. Run: python manage.py makemigrations")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py createsuperuser")
    print("4. Assign appropriate roles to users in Django admin")

if __name__ == "__main__":
    create_default_roles()