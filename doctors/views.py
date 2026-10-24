from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import DoctorProfile
from .serializers import DoctorProfileSerializer, DoctorProfileUpdateSerializer


class DoctorListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        queryset = DoctorProfile.objects.filter(
            user__is_deleted=False,
            user__is_active=True
        ).select_related('user')

        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search) |
                Q(specialization__icontains=search) |
                Q(hospital_name__icontains=search) |
                Q(location__icontains=search) |
                Q(qualifications__icontains=search)
            )

        specialization = request.query_params.get('specialization', '').strip()
        if specialization and specialization.lower() != 'all':
            queryset = queryset.filter(specialization__iexact=specialization)

        serializer = DoctorProfileSerializer(queryset, many=True)
        return Response(serializer.data)


class DoctorDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            doctor = DoctorProfile.objects.select_related('user').get(
                pk=pk,
                user__is_deleted=False,
                user__is_active=True
            )
        except DoctorProfile.DoesNotExist:
            return Response({'error': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoctorProfileSerializer(doctor)
        today = timezone.localdate()
        # include upcoming available slots
        available_slots = doctor.slots.filter(
            is_booked=False,
            is_active=True,
            date__gte=today
        ).order_by('date', 'start_time')

        slots_data = [
            {
                'id': slot.id,
                'date': slot.date,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'duration_minutes': slot.duration_minutes,
                'consultation_fee': str(slot.consultation_fee or doctor.consultation_fee),
            }
            for slot in available_slots
        ]

        data = serializer.data
        data['available_slots'] = slots_data
        return Response(data)


class DoctorProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'DOCTOR' or not hasattr(request.user, 'doctor_profile'):
            return Response({'error': 'Only doctors can access this resource.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = DoctorProfileSerializer(request.user.doctor_profile)
        return Response(serializer.data)

    def put(self, request):
        if request.user.role != 'DOCTOR' or not hasattr(request.user, 'doctor_profile'):
            return Response({'error': 'Only doctors can access this resource.'}, status=status.HTTP_403_FORBIDDEN)
        doctor = request.user.doctor_profile
        serializer = DoctorProfileUpdateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Doctor profile updated successfully.',
                'doctor': DoctorProfileSerializer(doctor).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorSpecializationsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        specs = DoctorProfile.objects.filter(
            user__is_deleted=False,
            user__is_active=True
        ).values_list('specialization', flat=True).distinct()
        cleaned_specs = sorted(list(set(s for s in specs if s)))
        return Response(cleaned_specs)
