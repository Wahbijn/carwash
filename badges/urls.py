from django.urls import path
from . import views

urlpatterns = [
    path('', views.badges_gallery, name='badges-gallery'),
    path('mark-seen/', views.mark_badges_seen, name='badges-mark-seen'),
]
