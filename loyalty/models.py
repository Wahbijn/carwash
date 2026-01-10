from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class LoyaltyProfile(models.Model):
    """User loyalty profile with points and tier"""
    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loyalty'
    )
    points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze')
    total_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.points} pts ({self.tier})"

    def update_tier(self):
        """Auto-update tier based on total earned points"""
        if self.total_earned >= 1000:
            self.tier = 'platinum'
        elif self.total_earned >= 500:
            self.tier = 'gold'
        elif self.total_earned >= 200:
            self.tier = 'silver'
        else:
            self.tier = 'bronze'
        self.save(update_fields=['tier'])

    def add_points(self, amount, reason=""):
        """Add points and update tier"""
        self.points += amount
        self.total_earned += amount
        self.save()
        self.update_tier()

        PointTransaction.objects.create(
            profile=self,
            amount=amount,
            transaction_type='earn',
            reason=reason
        )

    def deduct_points(self, amount, reason=""):
        """Deduct points (for redemptions)"""
        if self.points >= amount:
            self.points -= amount
            self.save(update_fields=['points'])

            PointTransaction.objects.create(
                profile=self,
                amount=-amount,
                transaction_type='spend',
                reason=reason
            )
            return True
        return False


class Reward(models.Model):
    """Redeemable rewards"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    points_cost = models.IntegerField(validators=[MinValueValidator(1)])
    icon = models.CharField(max_length=50, default='🎁')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['points_cost']

    def __str__(self):
        return f"{self.name} ({self.points_cost} pts)"


class Redemption(models.Model):
    """Track when users redeem rewards"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    points_spent = models.IntegerField()
    redeemed_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-redeemed_at']

    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"


class PointTransaction(models.Model):
    """Transaction log for points"""
    TRANSACTION_TYPES = [
        ('earn', 'Earned'),
        ('spend', 'Spent'),
    ]

    profile = models.ForeignKey(LoyaltyProfile, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.amount > 0 else ''
        return f"{self.profile.user.username}: {sign}{self.amount} pts - {self.reason}"
