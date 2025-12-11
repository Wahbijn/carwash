from django.urls import include, path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),
    path('accounts/', include('accounts.urls')),
    path('signup/', views.signup, name='register')

]
