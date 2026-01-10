from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import ProgrammingError, OperationalError
from django.db.models import Count, Sum

from wash.models import Booking
from .models import Badge, UserBadge


def check_and_unlock_badge(user, condition_type, current_value):
    """Check if user should unlock any badges"""
    try:
        badges = Badge.objects.filter(
            is_active=True,
            condition_type=condition_type,
            condition_value__lte=current_value
        )
        
        for badge in badges:
            UserBadge.objects.get_or_create(user=user, badge=badge)
    except (ProgrammingError, OperationalError):
        pass


@receiver(post_save, sender=Booking)
def check_booking_badges(sender, instance, created, **kwargs):
    """Check and unlock badges based on booking activity"""
    try:
        user = instance.user
        
        # Count total bookings (excluding cancelled)
        total_bookings = Booking.objects.filter(
            user=user,
            status__in=['pending', 'confirmed', 'done']
        ).count()
        
        # Check booking count badges
        check_and_unlock_badge(user, 'total_bookings', total_bookings)
        
        # Count completed bookings
        completed_bookings = Booking.objects.filter(
            user=user,
            status='done'
        ).count()
        check_and_unlock_badge(user, 'completed_bookings', completed_bookings)
        
        # Calculate total spent
        total_spent = Booking.objects.filter(
            user=user,
            status='done'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        check_and_unlock_badge(user, 'total_spent', int(total_spent))
        
        # Check loyalty tier badge
        if hasattr(user, 'loyalty'):
            tier_values = {'bronze': 1, 'silver': 2, 'gold': 3, 'platinum': 4}
            tier_value = tier_values.get(user.loyalty.tier, 0)
            check_and_unlock_badge(user, 'loyalty_tier', tier_value)
            
    except (ProgrammingError, OperationalError):
        pass
