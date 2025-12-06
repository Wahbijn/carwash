from django.urls import path
from .views import BookingUpdateView, ServiceListView, ServiceCreateView, BookingCreateView, BookingListView, BookingDetailView, vehicle_create
from django.urls import path
from .views import BookingListView, BookingCreateView, BookingDetailView, BookingCancelView
from . import views

urlpatterns = [
    path('services/', ServiceListView.as_view(), name='services-list'),
    path('services/new/', ServiceCreateView.as_view(), name='services-create'),  # 👈 AJOUT
    path('bookings/new/', BookingCreateView.as_view(), name='bookings-create'),
    path('bookings/',     BookingListView.as_view(),  name='bookings-list'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='bookings-detail'),
    path('vehicles/new/', vehicle_create, name='vehicles-new'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='bookings-cancel'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel, name='bookings-cancel'),
    path('bookings/<int:pk>/cancel/', BookingCancelView.as_view(), name='bookings-cancel'),
     path('bookings/<int:pk>/edit/', BookingUpdateView.as_view(), name='bookings-edit'),
    path('bookings/<int:pk>/cancel/', BookingCancelView.as_view(), name='bookings-cancel'),
    path('bookings/<int:pk>/edit/', BookingUpdateView.as_view(), name='bookings-edit'),

]
