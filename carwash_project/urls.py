"""
URL configuration for carwash_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# carwash_project/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from wash import views as wash_views
from accounts import views as accounts_views

urlpatterns = [
    #  Register your custom admin pages FIRST
    path("", include("wash.urls")),  # your app URLs FIRST

    #  Default Django Admin LAST
    path("admin/", admin.site.urls),
    path('', include('wash.urls')),
    path('accounts/signup/', accounts_views.signup_view, name='signup'),
    path('accounts/profile/', accounts_views.profile_view, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('loyalty/', include('loyalty.urls')),
    path('badges/', include('badges.urls')),
    path('bookings/new/', wash_views.BookingCreateView.as_view(), name='bookings-create'),
    path('bookings/<int:pk>/cancel/', wash_views.booking_cancel, name='bookings-cancel'),
    path("", wash_views.home, name="home"),

]

# dev: serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


