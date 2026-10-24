from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import AppointmentSlot, AppointmentBooking
from .serializers import AppointmentSlotSerializer, AppointmentBookingSerializer
from doctors.models import DoctorProfile


class SlotListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        doctor_id = request.query_params.get('doctor_id')
        date_str = request.query_params.get('date')

        # If doctor logged in and querying own slots without doctor_id param
        if request.user.is_authenticated and request.user.role == 'DOCTOR' and not doctor_id:
            try:
                doctor = request.user.doctor_profile
                slots = AppointmentSlot.objects.filter(doctor=doctor, is_active=True).order_by('date', 'start_time')
                if date_str:
                    slots = slots.filter(date=date_str)
                serializer = AppointmentSlotSerializer(slots, many=True)
                return Response(serializer.data)
            except DoctorProfile.DoesNotExist:
                return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not doctor_id:
            return Response({'error': 'doctor_id query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Public / Patient query for a specific doctor's slots
        today = timezone.localdate()
        slots = AppointmentSlot.objects.filter(
            doctor_id=doctor_id,
            is_booked=False,
            is_active=True,
            date__gte=today
        ).order_by('date', 'start_time')

        if date_str:
            slots = slots.filter(date=date_str)

        serializer = AppointmentSlotSerializer(slots, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'DOCTOR' or not hasattr(request.user, 'doctor_profile'):
            return Response({'error': 'Only doctors can create appointment slots.'}, status=status.HTTP_403_FORBIDDEN)

        doctor = request.user.doctor_profile
        serializer = AppointmentSlotSerializer(data=request.data)
        if serializer.is_valid():
            slot_date = serializer.validated_data['date']
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['end_time']

            # Check for overlapping slots for this doctor
            overlap = AppointmentSlot.objects.filter(
                doctor=doctor,
                date=slot_date,
                is_active=True,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()

            if overlap:
                return Response(
                    {'error': 'This time slot overlaps with an existing slot in your schedule.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            consultation_fee = serializer.validated_data.get('consultation_fee') or doctor.consultation_fee
            slot = serializer.save(doctor=doctor, consultation_fee=consultation_fee)
            return Response(AppointmentSlotSerializer(slot).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SlotDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_slot(self, pk, user):
        try:
            doctor = user.doctor_profile
            return AppointmentSlot.objects.get(pk=pk, doctor=doctor)
        except (DoctorProfile.DoesNotExist, AppointmentSlot.DoesNotExist):
            return None

    def put(self, request, pk):
        if request.user.role != 'DOCTOR':
            return Response({'error': 'Only doctors can edit appointment slots.'}, status=status.HTTP_403_FORBIDDEN)

        slot = self.get_slot(pk, request.user)
        if not slot:
            return Response({'error': 'Slot not found or unauthorized.'}, status=status.HTTP_404_NOT_FOUND)

        if slot.is_booked:
            return Response({'error': 'Cannot modify an appointment slot that is already booked.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AppointmentSlotSerializer(slot, data=request.data, partial=True)
        if serializer.is_valid():
            slot_date = serializer.validated_data.get('date', slot.date)
            start_time = serializer.validated_data.get('start_time', slot.start_time)
            end_time = serializer.validated_data.get('end_time', slot.end_time)

            overlap = AppointmentSlot.objects.filter(
                doctor=slot.doctor,
                date=slot_date,
                is_active=True,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(pk=slot.pk).exists()

            if overlap:
                return Response(
                    {'error': 'This time slot overlaps with another slot in your schedule.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            updated_slot = serializer.save()
            return Response(AppointmentSlotSerializer(updated_slot).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.role != 'DOCTOR':
            return Response({'error': 'Only doctors can delete appointment slots.'}, status=status.HTTP_403_FORBIDDEN)

        slot = self.get_slot(pk, request.user)
        if not slot:
            return Response({'error': 'Slot not found or unauthorized.'}, status=status.HTTP_404_NOT_FOUND)

        if slot.is_booked:
            return Response(
                {'error': 'Cannot delete a slot that has an active booking. Cancel or complete the appointment first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        slot.delete()
        return Response({'message': 'Appointment slot deleted successfully.'}, status=status.HTTP_200_OK)


class BookAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != 'PATIENT':
            return Response({'error': 'Only registered patients can book appointments.'}, status=status.HTTP_403_FORBIDDEN)

        slot_id = request.data.get('slot_id')
        patient_notes = request.data.get('patient_notes', '').strip()

        if not slot_id:
            return Response({'error': 'slot_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Atomic transaction with database row locking prevents concurrent double-booking
            with transaction.atomic():
                slot = AppointmentSlot.objects.select_for_update().get(id=slot_id)

                if slot.is_booked or not slot.is_active:
                    return Response(
                        {'error': 'This appointment slot has already been booked or is no longer available.'},
                        status=status.HTTP_409_CONFLICT
                    )

                if slot.date < timezone.localdate():
                    return Response(
                        {'error': 'Cannot book an appointment slot for a past date.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Mark slot as booked
                slot.is_booked = True
                slot.save()

                booking = AppointmentBooking.objects.create(
                    patient=request.user,
                    doctor=slot.doctor,
                    slot=slot,
                    status='PENDING',
                    patient_notes=patient_notes
                )

                return Response(
                    AppointmentBookingSerializer(booking).data,
                    status=status.HTTP_201_CREATED
                )

        except AppointmentSlot.DoesNotExist:
            return Response({'error': 'Appointment slot not found.'}, status=status.HTTP_404_NOT_FOUND)


class AppointmentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        status_param = request.query_params.get('status')

        if user.role == 'PATIENT':
            bookings = AppointmentBooking.objects.filter(patient=user)
        elif user.role == 'DOCTOR' and hasattr(user, 'doctor_profile'):
            bookings = AppointmentBooking.objects.filter(doctor=user.doctor_profile)
        elif user.role == 'ADMIN' or user.is_staff:
            bookings = AppointmentBooking.objects.all()
        else:
            return Response({'error': 'Unauthorized to view appointments.'}, status=status.HTTP_403_FORBIDDEN)

        if status_param and status_param.upper() != 'ALL':
            bookings = bookings.filter(status=status_param.upper())

        bookings = bookings.select_related('patient', 'doctor__user', 'slot')
        serializer = AppointmentBookingSerializer(bookings, many=True)
        return Response(serializer.data)


class AppointmentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            booking = AppointmentBooking.objects.select_related('patient', 'doctor__user', 'slot').get(pk=pk)
        except AppointmentBooking.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        is_patient = booking.patient == user
        is_doctor = hasattr(user, 'doctor_profile') and booking.doctor == user.doctor_profile
        is_admin = user.role == 'ADMIN' or user.is_staff

        if not (is_patient or is_doctor or is_admin):
            return Response({'error': 'You do not have permission to view this appointment.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentBookingSerializer(booking)
        return Response(serializer.data)


class CancelAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = AppointmentBooking.objects.select_related('patient', 'doctor__user', 'slot').get(pk=pk)
        except AppointmentBooking.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        is_patient = booking.patient == user
        is_doctor = hasattr(user, 'doctor_profile') and booking.doctor == user.doctor_profile

        if not (is_patient or is_doctor or user.is_staff):
            return Response({'error': 'You are not authorized to cancel this appointment.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status in ['CANCELLED', 'REJECTED']:
            return Response({'error': f'Appointment is already {booking.status.lower()}.'}, status=status.HTTP_400_BAD_REQUEST)

        if booking.status == 'COMPLETED':
            return Response({'error': 'Cannot cancel a completed appointment.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            booking.status = 'CANCELLED'
            booking.cancellation_reason = request.data.get('reason', 'Cancelled by user').strip()
            booking.save()

            # Free up the slot so others or the doctor can use it
            slot = booking.slot
            slot.is_booked = False
            slot.save()

        return Response({
            'message': 'Appointment cancelled successfully.',
            'booking': AppointmentBookingSerializer(booking).data
        })


class UpdateAppointmentStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != 'DOCTOR' or not hasattr(request.user, 'doctor_profile'):
            return Response({'error': 'Only the assigned doctor can update appointment status.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            booking = AppointmentBooking.objects.select_related('slot', 'doctor').get(pk=pk, doctor=request.user.doctor_profile)
        except AppointmentBooking.DoesNotExist:
            return Response({'error': 'Appointment not found or unauthorized.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status', '').upper()
        allowed = ['ACCEPTED', 'REJECTED', 'COMPLETED']
        if new_status not in allowed:
            return Response({'error': f"Invalid status. Must be one of {allowed}."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            booking.status = new_status
            if 'doctor_notes' in request.data:
                booking.doctor_notes = request.data.get('doctor_notes', '').strip()
            booking.save()

            # If rejected, free up the slot
            if new_status == 'REJECTED':
                slot = booking.slot
                slot.is_booked = False
                slot.save()

        return Response({
            'message': f'Appointment marked as {new_status}.',
            'booking': AppointmentBookingSerializer(booking).data
        })
