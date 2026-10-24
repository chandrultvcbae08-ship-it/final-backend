from django.db import models
from django.conf import settings
from doctors.models import DoctorProfile


class AppointmentSlot(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_booked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'date', 'start_time'],
                name='unique_doctor_slot'
            )
        ]

    def __str__(self):
        return f"{self.doctor.user.full_name} | {self.date} {self.start_time}-{self.end_time}"


class AppointmentBooking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='patient_appointments'
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.PROTECT,
        related_name='doctor_appointments'
    )
    slot = models.OneToOneField(
        AppointmentSlot,
        on_delete=models.PROTECT,
        related_name='booking'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    patient_notes = models.TextField(blank=True, default='', help_text="Symptoms / reason for appointment")
    doctor_notes = models.TextField(blank=True, default='', help_text="Doctor notes / diagnosis remarks")
    cancellation_reason = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id}: {self.patient.full_name} with {self.doctor.user.full_name} ({self.status})"
