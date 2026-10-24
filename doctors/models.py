from django.db import models
from django.conf import settings


class DoctorProfile(models.Model):
    SPECIALIZATION_CHOICES = [
        ('Cardiologist', 'Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('Neurologist', 'Neurologist'),
        ('Pediatrician', 'Pediatrician'),
        ('General Physician', 'General Physician'),
        ('Orthopedic', 'Orthopedic'),
        ('Gynecologist', 'Gynecologist'),
        ('Ophthalmologist', 'Ophthalmologist'),
        ('Psychiatrist', 'Psychiatrist'),
        ('Dentist', 'Dentist'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES)
    qualifications = models.CharField(max_length=200, help_text="e.g. MBBS, MD")
    experience_years = models.PositiveIntegerField(default=1)
    hospital_name = models.CharField(max_length=200, help_text="Hospital or Clinic Name")
    location = models.CharField(max_length=200, default='Bangalore')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    bio = models.TextField(blank=True)
    profile_image = models.TextField(blank=True, default='')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8)
    total_reviews = models.PositiveIntegerField(default=15)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.full_name} - {self.specialization}"

    class Meta:
        ordering = ['-rating', 'experience_years']
