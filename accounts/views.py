from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .models import User, PatientProfile
from .serializers import (
    UserSerializer,
    PatientRegistrationSerializer,
    DoctorRegistrationSerializer,
    LoginSerializer,
    DeleteAccountSerializer,
    PatientProfileSerializer
)
from doctors.models import DoctorProfile
from doctors.serializers import DoctorProfileSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterPatientView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PatientRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                'message': 'Patient registration successful',
                'user': user_data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterDoctorView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = DoctorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            user_data = UserSerializer(user).data
            doctor_profile = DoctorProfileSerializer(user.doctor_profile).data
            return Response({
                'message': 'Doctor registration successful',
                'user': user_data,
                'doctor_profile': doctor_profile,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            user_data = UserSerializer(user).data
            
            response_payload = {
                'message': 'Login successful',
                'user': user_data,
                'tokens': tokens
            }

            if user.role == 'DOCTOR' and hasattr(user, 'doctor_profile'):
                response_payload['doctor_profile'] = DoctorProfileSerializer(user.doctor_profile).data

            return Response(response_payload, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSerializer(user).data
        if user.role == 'DOCTOR' and hasattr(user, 'doctor_profile'):
            data['doctor_profile'] = DoctorProfileSerializer(user.doctor_profile).data
        return Response(data)

    def put(self, request):
        user = request.user
        full_name = request.data.get('full_name')
        phone = request.data.get('phone')

        if full_name:
            user.full_name = full_name
        if phone is not None:
            user.phone = phone
        user.save()

        # Update patient profile if patient
        if user.role == 'PATIENT' and hasattr(user, 'patient_profile'):
            profile = user.patient_profile
            profile.date_of_birth = request.data.get('date_of_birth', profile.date_of_birth)
            profile.gender = request.data.get('gender', profile.gender)
            profile.blood_group = request.data.get('blood_group', profile.blood_group)
            profile.address = request.data.get('address', profile.address)
            profile.emergency_contact = request.data.get('emergency_contact', profile.emergency_contact)
            profile.medical_history = request.data.get('medical_history', profile.medical_history)
            profile.save()

        data = UserSerializer(user).data
        if user.role == 'DOCTOR' and hasattr(user, 'doctor_profile'):
            data['doctor_profile'] = DoctorProfileSerializer(user.doctor_profile).data

        return Response({
            'message': 'Profile updated successfully',
            'user': data
        })


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = DeleteAccountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        password = serializer.validated_data['password']
        if not user.check_password(password):
            return Response({'password': ['Incorrect password. Verification failed.']}, status=status.HTTP_400_BAD_REQUEST)

        # Blacklist tokens for this user
        try:
            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)
        except Exception:
            pass

        # If doctor, mark unbooked future slots inactive so they cannot be booked
        if user.role == 'DOCTOR' and hasattr(user, 'doctor_profile'):
            doctor = user.doctor_profile
            doctor.is_available = False
            doctor.save()
            doctor.slots.filter(is_booked=False).update(is_active=False)

        # Soft delete the user to preserve patient/doctor medical history & prescriptions
        user.soft_delete()

        return Response({
            'message': 'Your account has been successfully deactivated and deleted. Your medical records remain safely archived for regulatory compliance.',
            'status': 'deactivated'
        }, status=status.HTTP_200_OK)
