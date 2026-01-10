# ===============================
#         IMPORTS
# ===============================
from django.urls import path

from wash import views_users

# Views imported 
from .views import (
    BookingUpdateView, ServiceListView, ServiceCreateView,
    BookingCreateView, BookingListView, BookingDetailView, ServiceUpdateView,
    admin_dashboard, vehicle_create , BookingCancelView ,
    
)

from . import views


# ===============================
#         URL PATTERNS
# ===============================
urlpatterns = [

    # ============================
    #        SERVICES
    # ============================
    path('services/', ServiceListView.as_view(), name='services-list'),
    path('services/new/', ServiceCreateView.as_view(), name='services-create'),  # Create a new service


    # ============================
    #        BOOKINGS
    # ============================

    # Create booking
    path('bookings/new/', BookingCreateView.as_view(), name='bookings-create'),

    # List bookings
    path('bookings/', BookingListView.as_view(), name='bookings-list'),

    # Booking details
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='bookings-detail'),

    # Booking cancel (multiple duplicates kept as requested)
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='bookings-cancel'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel, name='bookings-cancel'),
    path('bookings/<int:pk>/cancel/', BookingCancelView.as_view(), name='bookings-cancel'),
    path('bookings/<int:pk>/edit/', BookingUpdateView.as_view(), name='bookings-edit'),
    path('bookings/<int:pk>/cancel/', BookingCancelView.as_view(), name='bookings-cancel'),
    path('bookings/<int:pk>/edit/', BookingUpdateView.as_view(), name='bookings-edit'),

    # ============================
    #        VEHICLES
    # ============================
    path('vehicles/new/', vehicle_create, name='vehicles-new'),
    path("vehicle/add/", vehicle_create, name="vehicle-create"),  # Duplicate kept intentionally


    # ============================
    #    CUSTOM ADMIN DASHBOARD
    # ============================
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path("admin/dashboard/", admin_dashboard, name="admin-dashboard"),  # Duplicate kept intentionally

    # ============================
    #    ADMIN USERS MANAGEMENT
    # ============================

    path("admin/users/", views_users.users_list, name="users-list"),
    path("admin/users/<int:user_id>/", views_users.user_detail, name="user-detail"),
    path("admin/users/<int:user_id>/edit/", views_users.user_edit, name="user-edit"),
    path("admin/users/<int:user_id>/toggle-active/", views_users.user_toggle_active, name="user-toggle-active"),
    path("admin/users/<int:user_id>/toggle-admin/", views_users.user_toggle_admin, name="user-toggle-admin"),
    path("admin/users/<int:user_id>/delete/", views_users.user_delete, name="user-delete"),


    # ============================
    #    SERVICES MANAGEMENT
    # ============================

    # EDIT service
    path("services/<int:pk>/edit/", views.ServiceUpdateView.as_view(), name="service-edit"),

    # DELETE service
    path("services/<int:pk>/delete/", views.service_delete, name="service-delete"),

    # ============================
    #    BOOKING MANAGEMENT
    # ============================
    path("admin/booking/<int:pk>/done/", views.booking_mark_done, name="booking-done"),

    


]
