from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, PatientProfile
from doctors.models import DoctorProfile


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['id', 'date_of_birth', 'gender', 'blood_group', 'address', 'emergency_contact', 'medical_history']


class UserSerializer(serializers.ModelSerializer):
    patient_profile = PatientProfileSerializer(read_only=True)
    doctor_id = serializers.SerializerMethodField()
    patient_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role', 'phone',
            'is_active', 'is_deleted', 'doctor_id', 'patient_id',
            'patient_profile'
        ]
        read_only_fields = ['id', 'role', 'is_active', 'is_deleted']

    def get_doctor_id(self, obj):
        if obj.role == 'DOCTOR' and hasattr(obj, 'doctor_profile'):
            return obj.doctor_profile.id
        return None

    def get_patient_id(self, obj):
        if obj.role == 'PATIENT' and hasattr(obj, 'patient_profile'):
            return obj.patient_profile.id
        return None


class PatientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    blood_group = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    emergency_contact = serializers.CharField(required=False, allow_blank=True)
    medical_history = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'full_name', 'email', 'password', 'phone',
            'date_of_birth', 'gender', 'blood_group', 'address',
            'emergency_contact', 'medical_history'
        ]

    def validate_email(self, value):
        normalized = value.lower().strip()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return normalized

    def create(self, validated_data):
        dob = validated_data.pop('date_of_birth', None)
        gender = validated_data.pop('gender', '')
        blood_group = validated_data.pop('blood_group', '')
        address = validated_data.pop('address', '')
        emergency_contact = validated_data.pop('emergency_contact', '')
        medical_history = validated_data.pop('medical_history', '')

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone=validated_data.get('phone', ''),
            role='PATIENT'
        )

        PatientProfile.objects.create(
            user=user,
            date_of_birth=dob,
            gender=gender,
            blood_group=blood_group,
            address=address,
            emergency_contact=emergency_contact,
            medical_history=medical_history
        )
        return user


class DoctorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    specialization = serializers.CharField()
    qualifications = serializers.CharField()
    experience_years = serializers.IntegerField(default=1)
    hospital_name = serializers.CharField()
    location = serializers.CharField(default='Bangalore')
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    bio = serializers.CharField(required=False, allow_blank=True)
    profile_image = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'full_name', 'email', 'password', 'phone',
            'specialization', 'qualifications', 'experience_years',
            'hospital_name', 'location', 'consultation_fee', 'bio',
            'profile_image'
        ]

    def validate_email(self, value):
        normalized = value.lower().strip()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return normalized

    def create(self, validated_data):
        specialization = validated_data.pop('specialization')
        qualifications = validated_data.pop('qualifications')
        experience_years = validated_data.pop('experience_years', 1)
        hospital_name = validated_data.pop('hospital_name')
        location = validated_data.pop('location', 'Bangalore')
        consultation_fee = validated_data.pop('consultation_fee', 500.00)
        bio = validated_data.pop('bio', '')
        profile_image = validated_data.pop('profile_image', '')

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone=validated_data.get('phone', ''),
            role='DOCTOR'
        )

        DoctorProfile.objects.create(
            user=user,
            specialization=specialization,
            qualifications=qualifications,
            experience_years=experience_years,
            hospital_name=hospital_name,
            location=location,
            consultation_fee=consultation_fee,
            bio=bio,
            profile_image=profile_image,
            rating=5.0,
            total_reviews=1
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email', '').lower().strip()
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Must provide both email and password.")

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if user.is_deleted or not user.is_active:
            raise serializers.ValidationError("This account has been deactivated or deleted.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        data['user'] = user
        return data


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    confirmation = serializers.BooleanField(required=True)

    def validate_confirmation(self, value):
        if not value:
            raise serializers.ValidationError("Please confirm account deletion.")
        return value
