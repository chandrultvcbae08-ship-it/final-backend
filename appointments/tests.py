from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta, time
from accounts.models import User
from doctors.models import DoctorProfile
from appointments.models import AppointmentSlot, AppointmentBooking


class SlotAndBookingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Doctor
        self.doctor_user = User.objects.create_user(
            email='dr.test@example.com',
            password='Password123!',
            full_name='Dr. Test',
            role='DOCTOR'
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Cardiologist',
            qualifications='MBBS, MD',
            hospital_name='Care Hospital',
            consultation_fee=500.00
        )

        # Create Patient 1
        self.patient1 = User.objects.create_user(
            email='patient1@example.com',
            password='Password123!',
            full_name='Patient One',
            role='PATIENT'
        )

        # Create Patient 2
        self.patient2 = User.objects.create_user(
            email='patient2@example.com',
            password='Password123!',
            full_name='Patient Two',
            role='PATIENT'
        )

    def test_doctor_slot_creation_and_overlap_prevention(self):
        # Login as doctor
        login_res = self.client.post(reverse('login'), {
            'email': 'dr.test@example.com',
            'password': 'Password123!'
        }, format='json')
        token = login_res.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        target_date = (timezone.localdate() + timedelta(days=2)).isoformat()

        # Create Slot
        url = reverse('slot-list-create')
        slot_data = {
            'date': target_date,
            'start_time': '10:00:00',
            'end_time': '10:30:00',
            'duration_minutes': 30
        }
        res = self.client.post(url, slot_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Attempt to create overlapping slot
        overlapping_data = {
            'date': target_date,
            'start_time': '10:15:00',
            'end_time': '10:45:00',
            'duration_minutes': 30
        }
        res_overlap = self.client.post(url, overlapping_data, format='json')
        self.assertEqual(res_overlap.status_code, status.HTTP_400_BAD_REQUEST)

    def test_appointment_booking_and_double_booking_prevention(self):
        target_date = timezone.localdate() + timedelta(days=3)
        slot = AppointmentSlot.objects.create(
            doctor=self.doctor_profile,
            date=target_date,
            start_time=time(14, 0),
            end_time=time(14, 30),
            consultation_fee=500.00,
            is_booked=False
        )

        # Patient 1 login and book
        p1_login = self.client.post(reverse('login'), {
            'email': 'patient1@example.com',
            'password': 'Password123!'
        }, format='json')
        p1_token = p1_login.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {p1_token}')

        book_url = reverse('book-appointment')
        book_res1 = self.client.post(book_url, {'slot_id': slot.id, 'patient_notes': 'Checkup'}, format='json')
        self.assertEqual(book_res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book_res1.data['status'], 'PENDING')

        # Verify slot is marked booked in DB
        slot.refresh_from_db()
        self.assertTrue(slot.is_booked)

        # Patient 2 tries to book the same slot -> must fail with conflict
        p2_login = self.client.post(reverse('login'), {
            'email': 'patient2@example.com',
            'password': 'Password123!'
        }, format='json')
        p2_token = p2_login.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {p2_token}')

        book_res2 = self.client.post(book_url, {'slot_id': slot.id, 'patient_notes': 'Second booking attempt'}, format='json')
        self.assertEqual(book_res2.status_code, status.HTTP_409_CONFLICT)
