from django.db import models
from django.conf import settings
from doctors.models import DoctorProfile
from appointments.models import AppointmentBooking


class Prescription(models.Model):
    appointment = models.OneToOneField(
        AppointmentBooking,
        on_delete=models.PROTECT,
        related_name='prescription'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='patient_prescriptions'
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.PROTECT,
        related_name='doctor_prescriptions'
    )
    diagnosis = models.TextField(help_text="Clinical diagnosis and symptoms assessment")
    notes = models.TextField(blank=True, default='', help_text="General medical advice, lifestyle changes or follow-up")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription #{self.id} for {self.patient.full_name} by Dr. {self.doctor.user.full_name}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items'
    )
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, help_text="e.g. 500mg, 1 tablet")
    frequency = models.CharField(max_length=100, help_text="e.g. Twice daily after meals (1-0-1)")
    duration = models.CharField(max_length=100, help_text="e.g. 5 days, 2 weeks")
    instructions = models.TextField(blank=True, default='', help_text="Special instructions e.g. drink plenty of water")

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage} ({self.frequency})"
