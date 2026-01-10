# wash/models.py
from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone


User = settings.AUTH_USER_MODEL   # string like "auth.User" or custom user model

class Service(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    duration_minutes = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=50)
    make = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.license_plate

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle = models.ForeignKey("Vehicle", null=True, blank=True, on_delete=models.SET_NULL)
    service = models.ForeignKey("Service", null=True, blank=True, on_delete=models.SET_NULL)

    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    #  THIS WAS MISSING
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    reminder_sent = models.BooleanField(default=False)
    ia_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username}"
    
    
    @property
    def scheduled_at(self):
        """
        Retourne un datetime timezone-aware représentant la date+heure programmée,
        ou None si date/time manquants.
        """
        if not self.scheduled_date or not self.scheduled_time:
            return None

        dt = datetime.combine(self.scheduled_date, self.scheduled_time)

        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_default_timezone())

        return dt
