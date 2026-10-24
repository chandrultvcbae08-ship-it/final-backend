from rest_framework import serializers
from .models import Prescription, PrescriptionItem
from appointments.models import AppointmentBooking


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = ['id', 'medicine_name', 'dosage', 'frequency', 'duration', 'instructions']


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, required=False)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    doctor_qualifications = serializers.CharField(source='doctor.qualifications', read_only=True)
    doctor_hospital = serializers.CharField(source='doctor.hospital_name', read_only=True)
    appointment_date = serializers.DateField(source='appointment.slot.date', read_only=True)
    appointment_time = serializers.TimeField(source='appointment.slot.start_time', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'appointment', 'patient', 'patient_name', 'patient_email', 'patient_phone',
            'doctor', 'doctor_name', 'doctor_specialization', 'doctor_qualifications', 'doctor_hospital',
            'appointment_date', 'appointment_time', 'diagnosis', 'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient', 'doctor', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        prescription = Prescription.objects.create(**validated_data)
        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)
        return prescription
