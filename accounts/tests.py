from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, PatientProfile
from doctors.models import DoctorProfile


class AuthenticationAndAccountTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient_data = {
            'full_name': 'Test Patient',
            'email': 'testpatient@example.com',
            'password': 'SecurePassword123!',
            'phone': '9876543210',
            'gender': 'Female',
            'blood_group': 'B+'
        }
        self.doctor_data = {
            'full_name': 'Dr. New Specialist',
            'email': 'dr.new@example.com',
            'password': 'SecureDoctorPassword123!',
            'phone': '9876543211',
            'specialization': 'Cardiologist',
            'qualifications': 'MBBS, MD',
            'experience_years': 6,
            'hospital_name': 'Apex Care Clinic',
            'location': 'Bangalore',
            'consultation_fee': 750.00
        }

    def test_patient_registration_and_login(self):
        # Register
        url = reverse('register-patient')
        res = self.client.post(url, self.patient_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', res.data)
        self.assertEqual(res.data['user']['role'], 'PATIENT')

        # Login
        login_url = reverse('login')
        login_res = self.client.post(login_url, {
            'email': 'testpatient@example.com',
            'password': 'SecurePassword123!'
        }, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_res.data['tokens'])

    def test_prevent_duplicate_email_registration(self):
        url = reverse('register-patient')
        self.client.post(url, self.patient_data, format='json')
        duplicate_res = self.client.post(url, self.patient_data, format='json')
        self.assertEqual(duplicate_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', duplicate_res.data)

    def test_doctor_registration(self):
        url = reverse('register-doctor')
        res = self.client.post(url, self.doctor_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user']['role'], 'DOCTOR')
        self.assertTrue(DoctorProfile.objects.filter(user__email='dr.new@example.com').exists())

    def test_account_deletion_soft_delete(self):
        # Register patient
        reg_url = reverse('register-patient')
        reg_res = self.client.post(reg_url, self.patient_data, format='json')
        access_token = reg_res.data['tokens']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        del_url = reverse('delete-account')

        # Attempt with wrong password
        fail_res = self.client.post(del_url, {'password': 'WrongPassword!', 'confirmation': True}, format='json')
        self.assertEqual(fail_res.status_code, status.HTTP_400_BAD_REQUEST)

        # Delete with correct password
        success_res = self.client.post(del_url, {'password': 'SecurePassword123!', 'confirmation': True}, format='json')
        self.assertEqual(success_res.status_code, status.HTTP_200_OK)

        # Verify soft delete
        user = User.objects.get(email='testpatient@example.com')
        self.assertTrue(user.is_deleted)
        self.assertFalse(user.is_active)

        # Ensure deleted user cannot log in
        self.client.credentials()  # Clear auth headers
        login_url = reverse('login')
        login_res = self.client.post(login_url, {
            'email': 'testpatient@example.com',
            'password': 'SecurePassword123!'
        }, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_400_BAD_REQUEST)
