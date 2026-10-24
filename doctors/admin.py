from django.contrib import admin
from .models import DoctorProfile


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'qualifications', 'experience_years', 'hospital_name', 'consultation_fee', 'rating', 'is_available')
    list_filter = ('specialization', 'is_available', 'location')
    search_fields = ('user__full_name', 'user__email', 'specialization', 'hospital_name')
