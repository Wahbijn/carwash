from django.urls import path
from . import views

urlpatterns = [
    path('', views.loyalty_dashboard, name='loyalty-dashboard'),
    path('redeem/<int:reward_id>/', views.redeem_reward, name='redeem-reward'),
]
