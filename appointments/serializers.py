from rest_framework import serializers
from .models import AppointmentSlot, AppointmentBooking
from doctors.models import DoctorProfile
from django.utils import timezone
from datetime import datetime, date, time


class AppointmentSlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    hospital_name = serializers.CharField(source='doctor.hospital_name', read_only=True)

    class Meta:
        model = AppointmentSlot
        fields = [
            'id', 'doctor', 'doctor_name', 'specialization', 'hospital_name',
            'date', 'start_time', 'end_time', 'duration_minutes',
            'consultation_fee', 'is_booked', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'doctor', 'is_booked', 'created_at']

    def validate(self, data):
        slot_date = data.get('date', getattr(self.instance, 'date', None))
        start_time = data.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = data.get('end_time', getattr(self.instance, 'end_time', None))

        if slot_date and slot_date < timezone.localdate():
            raise serializers.ValidationError({"date": "Cannot create appointment slots in the past."})

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})

        return data


class AppointmentBookingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    doctor_hospital = serializers.CharField(source='doctor.hospital_name', read_only=True)
    doctor_profile_image = serializers.CharField(source='doctor.profile_image', read_only=True)
    slot_date = serializers.DateField(source='slot.date', read_only=True)
    slot_start_time = serializers.TimeField(source='slot.start_time', read_only=True)
    slot_end_time = serializers.TimeField(source='slot.end_time', read_only=True)
    consultation_fee = serializers.SerializerMethodField()
    has_prescription = serializers.SerializerMethodField()

    class Meta:
        model = AppointmentBooking
        fields = [
            'id', 'patient', 'patient_name', 'patient_email', 'patient_phone',
            'doctor', 'doctor_name', 'doctor_specialization', 'doctor_hospital', 'doctor_profile_image',
            'slot', 'slot_date', 'slot_start_time', 'slot_end_time',
            'consultation_fee', 'status', 'patient_notes', 'doctor_notes',
            'cancellation_reason', 'has_prescription', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient', 'doctor', 'created_at', 'updated_at']

    def get_consultation_fee(self, obj):
        if obj.slot and obj.slot.consultation_fee is not None:
            return str(obj.slot.consultation_fee)
        return str(obj.doctor.consultation_fee)

    def get_has_prescription(self, obj):
        return hasattr(obj, 'prescription')
