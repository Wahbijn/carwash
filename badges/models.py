from django.db import models
from django.conf import settings


class Badge(models.Model):
    """Achievement badge that users can unlock"""
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='🏆')
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    condition_type = models.CharField(max_length=50)
    condition_value = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rarity', 'condition_value']

    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    """Tracks badges unlocked by users"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
