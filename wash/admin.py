from django.contrib import admin
from .models import Service, Vehicle, Booking

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name','price','duration_minutes')


admin.site.register(Vehicle)
admin.site.register(Booking)
