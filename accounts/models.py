from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def avatar_upload_to(instance, filename):
    return f"avatars/user_{instance.user.id}/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    email = models.EmailField(blank=True, null=True)   # <- add this

    def __str__(self):
        return self.display_name or str(self.user)