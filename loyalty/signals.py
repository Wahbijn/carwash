from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import ProgrammingError, OperationalError

from wash.models import Booking
from .models import LoyaltyProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_loyalty_profile(sender, instance, created, **kwargs):
    """Auto-create loyalty profile when user is created"""
    try:
        if created:
            LoyaltyProfile.objects.create(user=instance)
    except (ProgrammingError, OperationalError):
        pass


@receiver(post_save, sender=Booking)
def award_points_for_booking(sender, instance, created, **kwargs):
    """Award points when booking is marked as done"""
    if instance.status == 'done':
        try:
            profile, _ = LoyaltyProfile.objects.get_or_create(user=instance.user)
            
            if not hasattr(instance, '_points_awarded'):
                points = int(instance.total_price / 10)
                if points > 0:
                    profile.add_points(points, f"Réservation #{instance.pk} terminée")
                    instance._points_awarded = True
        except (ProgrammingError, OperationalError):
            pass
