from django.contrib import admin
from .models import AppointmentSlot, AppointmentBooking


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'duration_minutes', 'is_booked', 'is_active')
    list_filter = ('date', 'is_booked', 'is_active')
    search_fields = ('doctor__user__full_name',)


@admin.register(AppointmentBooking)
class AppointmentBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'slot', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__full_name', 'patient__email', 'doctor__user__full_name')
