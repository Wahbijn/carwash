from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Badge, UserBadge


@login_required
def badges_gallery(request):
    """Display all badges and user's progress"""
    all_badges = Badge.objects.filter(is_active=True)
    user_badge_ids = UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True)

    unlocked_badges = UserBadge.objects.filter(user=request.user).select_related('badge')

    badges_data = []
    for badge in all_badges:
        badges_data.append({
            'badge': badge,
            'unlocked': badge.id in user_badge_ids,
        })

    total_badges = all_badges.count()
    unlocked_count = unlocked_badges.count()
    progress_percent = int((unlocked_count / total_badges * 100)) if total_badges > 0 else 0

    new_badges_count = unlocked_badges.filter(is_new=True).count()

    return render(request, 'badges/gallery.html', {
        'badges_data': badges_data,
        'unlocked_badges': unlocked_badges,
        'total_badges': total_badges,
        'unlocked_count': unlocked_count,
        'progress_percent': progress_percent,
        'new_badges_count': new_badges_count,
    })


@login_required
def mark_badges_seen(request):
    """Mark all new badges as seen"""
    UserBadge.objects.filter(user=request.user, is_new=True).update(is_new=False)
    from django.shortcuts import redirect
    return redirect('badges-gallery')
