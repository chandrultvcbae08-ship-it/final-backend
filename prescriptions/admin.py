from django.contrib import admin
from .models import Prescription, PrescriptionItem


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment', 'created_at')
    search_fields = ('patient__full_name', 'doctor__user__full_name', 'diagnosis')
    inlines = [PrescriptionItemInline]
