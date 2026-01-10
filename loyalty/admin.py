from django.contrib import admin
from .models import LoyaltyProfile, Reward, Redemption, PointTransaction


@admin.register(LoyaltyProfile)
class LoyaltyProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'tier', 'total_earned', 'created_at']
    list_filter = ['tier', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_cost', 'icon', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward', 'points_spent', 'redeemed_at', 'used']
    list_filter = ['used', 'redeemed_at']
    search_fields = ['user__username', 'reward__name']
    readonly_fields = ['redeemed_at']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['profile', 'amount', 'transaction_type', 'reason', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['profile__user__username', 'reason']
    readonly_fields = ['created_at']
