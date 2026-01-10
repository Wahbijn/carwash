from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, SignupForm


# =====================================================
#                  SIGNUP VIEW
# =====================================================
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Compte créé avec succès. Connectez-vous pour continuer."
            )
            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "registration/signup.html", {"form": form})


# =====================================================
#               PROFILE DISPLAY VIEW
# =====================================================
@login_required
def profile_view(request):
    """
    Displays the profile page.
    If User.email exists → show it.
    Else → fallback to Profile.email if available.
    """
    user = request.user
    profile_email = None
    
    # Preferred: use email stored on User model
    if user.email:
        profile_email = user.email
    
    # Alternative: if Profile model exists and contains email
    elif hasattr(user, "profile") and getattr(user.profile, "email", None):
        profile_email = user.profile.email

    return render(request, "accounts/profile.html", {
        "user": user,
        "profile_email": profile_email,
    })


# =====================================================
#                PROFILE EDIT VIEW
# =====================================================
@login_required
def profile_edit(request):
    """
    Updates the user's email.
    If a Profile model exists → update Profile.email.
    Else → update User.email.
    """
    user = request.user

    if request.method == "POST":
        email = request.POST.get("email")

        if email:
            # If you have a Profile model
            if hasattr(user, "profile"):
                user.profile.email = email
                user.profile.save()

            # Default case: save to User model
            else:
                user.email = email
                user.save()

            messages.success(request, "Adresse e-mail mise à jour ✅")
            return redirect("profile")

        else:
            messages.error(request, "Veuillez entrer un e-mail valide.")

    return render(request, "accounts/profile_edit.html", {"user": user})
