# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import ProgrammingError, OperationalError
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Crée ou met à jour le profil utilisateur,
    sans planter si la table Profile n'existe pas encore.
    """
    try:
        if created:
            Profile.objects.create(user=instance)
        else:
            try:
                instance.profile.save()
            except Profile.DoesNotExist:
                Profile.objects.create(user=instance)
    except (ProgrammingError, OperationalError):
        pass
