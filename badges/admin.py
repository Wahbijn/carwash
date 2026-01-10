from django.contrib import admin
from .models import Badge, UserBadge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'rarity', 'condition_type', 'condition_value', 'is_active']
    list_filter = ['rarity', 'is_active', 'condition_type']
    search_fields = ['name', 'description']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'unlocked_at', 'is_new']
    list_filter = ['is_new', 'unlocked_at', 'badge__rarity']
    search_fields = ['user__username', 'badge__name']
    readonly_fields = ['unlocked_at']
