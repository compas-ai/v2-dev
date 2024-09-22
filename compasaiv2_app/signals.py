from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
import random
import string, time, csv, re

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Generate a random referral code
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        # Check if a Profile already exists for this User
        profile, created = Profile.objects.get_or_create(user=instance)

        # Set the username if it is not already set
        if instance.username:
            username = re.sub(r'[^\w]', '_', instance.username)
            instance.username = username
            instance.save()
            profile.username = username
        else:
            username = ''
            if instance.email:
                username, _ = instance.email.split('@')
                username = re.sub(r'[^\w]', '_', username)
            if username:
                profile.username = username + code
            else:
                profile.username = f"{instance.first_name} {instance.last_name} {code}".strip()

        # Set the display name (first name + last name) or default to username
        if instance.first_name or instance.last_name:
            profile.display_name = f"{instance.first_name} {instance.last_name}".strip()
        else:
            profile.display_name = profile.username

        # Set the email for the profile
        if instance.email:
            profile.email = instance.email

        # Save the profile with the new fields
        profile.is_confirmed = True
        profile.save()

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
#     print("profile saved")
