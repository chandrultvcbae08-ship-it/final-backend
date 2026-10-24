from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .models import Prescription, PrescriptionItem
from .serializers import PrescriptionSerializer
from appointments.models import AppointmentBooking


class PrescriptionListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'PATIENT':
            prescriptions = Prescription.objects.filter(patient=user)
        elif user.role == 'DOCTOR' and hasattr(user, 'doctor_profile'):
            prescriptions = Prescription.objects.filter(doctor=user.doctor_profile)
        elif user.role == 'ADMIN' or user.is_staff:
            prescriptions = Prescription.objects.all()
        else:
            return Response({'error': 'Unauthorized to view prescriptions.'}, status=status.HTTP_403_FORBIDDEN)

        prescriptions = prescriptions.select_related(
            'patient', 'doctor__user', 'appointment__slot'
        ).prefetch_related('items')

        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'DOCTOR' or not hasattr(request.user, 'doctor_profile'):
            return Response({'error': 'Only doctors can write prescriptions.'}, status=status.HTTP_403_FORBIDDEN)

        doctor = request.user.doctor_profile
        appointment_id = request.data.get('appointment')

        if not appointment_id:
            return Response({'error': 'Appointment ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            appointment = AppointmentBooking.objects.get(pk=appointment_id, doctor=doctor)
        except AppointmentBooking.DoesNotExist:
            return Response({'error': 'Appointment not found or unauthorized.'}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(appointment, 'prescription'):
            return Response({'error': 'A prescription already exists for this appointment.'}, status=status.HTTP_400_BAD_REQUEST)

        diagnosis = request.data.get('diagnosis', '').strip()
        notes = request.data.get('notes', '').strip()
        items_data = request.data.get('items', [])

        if not diagnosis:
            return Response({'error': 'Diagnosis is required.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Mark appointment as completed
            appointment.status = 'COMPLETED'
            if notes and not appointment.doctor_notes:
                appointment.doctor_notes = notes
            appointment.save()

            prescription = Prescription.objects.create(
                appointment=appointment,
                patient=appointment.patient,
                doctor=doctor,
                diagnosis=diagnosis,
                notes=notes
            )

            for item in items_data:
                med_name = item.get('medicine_name', '').strip()
                if med_name:
                    PrescriptionItem.objects.create(
                        prescription=prescription,
                        medicine_name=med_name,
                        dosage=item.get('dosage', '').strip(),
                        frequency=item.get('frequency', '').strip(),
                        duration=item.get('duration', '').strip(),
                        instructions=item.get('instructions', '').strip(),
                    )

        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PrescriptionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            prescription = Prescription.objects.select_related(
                'patient', 'doctor__user', 'appointment__slot'
            ).prefetch_related('items').get(pk=pk)
        except Prescription.DoesNotExist:
            return Response({'error': 'Prescription not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        is_patient = prescription.patient == user
        is_doctor = hasattr(user, 'doctor_profile') and prescription.doctor == user.doctor_profile
        is_admin = user.role == 'ADMIN' or user.is_staff

        if not (is_patient or is_doctor or is_admin):
            return Response({'error': 'Unauthorized to view this prescription.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data)


class PrescriptionByAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, appointment_id):
        try:
            prescription = Prescription.objects.select_related(
                'patient', 'doctor__user', 'appointment__slot'
            ).prefetch_related('items').get(appointment_id=appointment_id)
        except Prescription.DoesNotExist:
            return Response({'error': 'No prescription found for this appointment.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        is_patient = prescription.patient == user
        is_doctor = hasattr(user, 'doctor_profile') and prescription.doctor == user.doctor_profile
        is_admin = user.role == 'ADMIN' or user.is_staff

        if not (is_patient or is_doctor or is_admin):
            return Response({'error': 'Unauthorized to view this prescription.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data)
