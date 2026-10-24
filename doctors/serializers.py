from rest_framework import serializers
from .models import DoctorProfile
from django.utils import timezone


class DoctorProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    available_slots_count = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user_id', 'full_name', 'email', 'phone',
            'specialization', 'qualifications', 'experience_years',
            'hospital_name', 'location', 'consultation_fee', 'bio',
            'profile_image', 'rating', 'total_reviews', 'is_available',
            'available_slots_count', 'created_at'
        ]

    def get_available_slots_count(self, obj):
        today = timezone.localdate()
        return obj.slots.filter(is_booked=False, is_active=True, date__gte=today).count()


class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', required=False)
    phone = serializers.CharField(source='user.phone', required=False)

    class Meta:
        model = DoctorProfile
        fields = [
            'full_name', 'phone', 'specialization', 'qualifications',
            'experience_years', 'hospital_name', 'location',
            'consultation_fee', 'bio', 'profile_image', 'is_available'
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            if 'full_name' in user_data:
                user.full_name = user_data['full_name']
            if 'phone' in user_data:
                user.phone = user_data['phone']
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
