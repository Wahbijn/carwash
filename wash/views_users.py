# wash/views_users.py
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Booking


# Only staff users can access user management
def admin_only(view):
    return user_passes_test(lambda u: u.is_staff)(view)


# ================================
#       USERS LIST
# ================================
@admin_only
def users_list(request):
    search = request.GET.get("search", "")

    users = User.objects.annotate(
        total_bookings=Count("booking")
    )

    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )

    return render(request, "wash/users_list.html", {
        "users": users,
        "search": search,
    })


# ================================
#       USER DETAIL
# ================================
@admin_only
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    bookings = Booking.objects.filter(user=user)

    return render(request, "wash/user_detail.html", {
        "user_obj": user,
        "bookings": bookings
    })


# ================================
#       USER EDIT
# ================================
@admin_only
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        if username:
            user.username = username

        if email:
            user.email = email

        user.save()
        messages.success(request, "Utilisateur mis à jour.")
        return redirect("user-detail", user_id=user.id)

    return render(request, "wash/user_edit.html", {"user_obj": user})


# ================================
#   USER ACTIVATE / DEACTIVATE
# ================================
@admin_only
def user_toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)

    user.is_active = not user.is_active
    user.save()

    if user.is_active:
        messages.success(request, f"{user.username} a été activé.")
    else:
        messages.warning(request, f"{user.username} a été désactivé.")

    return redirect("users-list")


# ================================
#   MAKE / REMOVE ADMIN
# ================================
@admin_only
def user_toggle_admin(request, user_id):
    user = get_object_or_404(User, id=user_id)

    user.is_staff = not user.is_staff
    user.save()

    if user.is_staff:
        messages.success(request, f"{user.username} est maintenant administrateur.")
    else:
        messages.warning(request, f"{user.username} n'est plus administrateur.")

    return redirect("user-detail", user_id=user.id)


# ================================
#      DELETE USER
# ================================
@admin_only
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.delete()
        messages.error(request, "Utilisateur supprimé définitivement.")
        return redirect("users-list")

    return render(request, "wash/user_delete_confirm.html", {
        "user_obj": user
    })
