from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, SignupForm

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Compte créé. Connectez-vous pour continuer.")
            return redirect(reverse_lazy('login'))
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile_view(request):
    """
    Simple profile page showing email (from User or Profile) + link to edit.
    """
    user = request.user
    profile_email = None
    if getattr(user, "email", None):
        profile_email = user.email
    elif getattr(user, "profile", None) and getattr(user.profile, "email", None):
        profile_email = user.profile.email

    return render(request, "accounts/profile.html", {
        "user": user,
        "profile_email": profile_email,
    })


@login_required
def profile_edit(request):
    user = request.user
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            if hasattr(user, "profile"):
                user.profile.email = email
                user.profile.save()
            else:
                user.email = email
                user.save()
            messages.success(request, "Adresse e-mail mise à jour ✅")
            return redirect("profile")  # redirect to profile view
        else:
            messages.error(request, "Veuillez entrer un e-mail valide.")
    return render(request, "accounts/profile_edit.html", {"user": user})