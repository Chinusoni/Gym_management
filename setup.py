#!/usr/bin/env python
"""
Gym Management Setup Script
Run this once to initialize the database and create an admin user.
Usage: python setup.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymmanager.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from gym.models import GymSettings, MembershipPlan

print("\n🏋️  Gym Management System — Setup\n" + "="*40)

# Run migrations
print("\n[1/4] Running migrations...")
call_command('migrate', verbosity=0)
print("      ✅ Database ready")

# Create gym settings
print("\n[2/4] Setting up gym profile...")
gym_name = input("      Enter your gym name (default: Iron Forge Gym): ").strip() or "Iron Forge Gym"
owner_name = input("      Enter owner name (default: Admin): ").strip() or "Admin"
phone = input("      Phone number (optional): ").strip()
email = input("      Email (optional): ").strip()

gs, _ = GymSettings.objects.get_or_create(pk=1)
gs.gym_name = gym_name
gs.owner_name = owner_name
gs.phone_number = phone
gs.email = email
gs.save()
print(f"      ✅ Gym profile saved: {gym_name}")

# Create default plans
print("\n[3/4] Creating default membership plans...")
default_plans = [
    ("Monthly",   1,  1500, "Full access, 1 month"),
    ("Quarterly", 3,  3999, "Full access, 3 months — save ₹501"),
    ("Annual",   12, 12999, "Full access, 12 months — best value"),
]
for name, months, price, desc in default_plans:
    plan, created = MembershipPlan.objects.get_or_create(
        name=name,
        defaults={'duration_months': months, 'price': price, 'description': desc}
    )
    status = "created" if created else "already exists"
    print(f"      {'✅' if created else '—'} {name} plan ({status})")

# Create admin user
print("\n[4/4] Creating admin user...")
username = input("      Admin username (default: admin): ").strip() or "admin"
password = input("      Admin password (default: admin123): ").strip() or "admin123"

if User.objects.filter(username=username).exists():
    print(f"      — User '{username}' already exists.")
else:
    User.objects.create_superuser(username=username, email=email or '', password=password)
    print(f"      ✅ Admin user '{username}' created")

print("\n" + "="*40)
print("🚀  Setup complete!\n")
print(f"   Run:  python manage.py runserver")
print(f"   Then open:  http://127.0.0.1:8000/")
print(f"   Admin panel: http://127.0.0.1:8000/admin-panel/")
print(f"   Username: {username}")
print(f"   Password: {password}")
print()
