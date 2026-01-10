from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LoyaltyProfile, Reward, Redemption


@login_required
def loyalty_dashboard(request):
    """User loyalty dashboard"""
    profile, created = LoyaltyProfile.objects.get_or_create(user=request.user)

    tier_info = {
        'bronze': {'next': 'Silver', 'needed': 200 - profile.total_earned if profile.total_earned < 200 else 0},
        'silver': {'next': 'Gold', 'needed': 500 - profile.total_earned if profile.total_earned < 500 else 0},
        'gold': {'next': 'Platinum', 'needed': 1000 - profile.total_earned if profile.total_earned < 1000 else 0},
        'platinum': {'next': None, 'needed': 0},
    }

    available_rewards = Reward.objects.filter(is_active=True)
    recent_transactions = profile.transactions.all()[:5]
    my_redemptions = Redemption.objects.filter(user=request.user, used=False)[:5]

    return render(request, 'loyalty/dashboard.html', {
        'profile': profile,
        'tier_info': tier_info.get(profile.tier, {}),
        'available_rewards': available_rewards,
        'recent_transactions': recent_transactions,
        'my_redemptions': my_redemptions,
    })


@login_required
def redeem_reward(request, reward_id):
    """Redeem a reward"""
    reward = get_object_or_404(Reward, pk=reward_id, is_active=True)
    profile, created = LoyaltyProfile.objects.get_or_create(user=request.user)

    if profile.points >= reward.points_cost:
        if profile.deduct_points(reward.points_cost, f"Échangé: {reward.name}"):
            Redemption.objects.create(
                user=request.user,
                reward=reward,
                points_spent=reward.points_cost
            )
            messages.success(request, f"Félicitations! Vous avez échangé {reward.name}")
        else:
            messages.error(request, "Erreur lors de l'échange")
    else:
        messages.error(request, "Points insuffisants pour cet échange")

    return redirect('loyalty-dashboard')
