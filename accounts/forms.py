from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'avatar']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Nom affiché (facultatif)'}),
        }

class SignupForm(UserCreationForm):
    # ajouter email si tu veux
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
