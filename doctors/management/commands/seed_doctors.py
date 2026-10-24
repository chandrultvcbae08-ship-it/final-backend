from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time, date
from accounts.models import User, PatientProfile
from doctors.models import DoctorProfile
from appointments.models import AppointmentSlot, AppointmentBooking
from prescriptions.models import Prescription, PrescriptionItem


class Command(BaseCommand):
    help = 'Seeds database with 5 specified sample doctors, appointment slots, and demo patient records'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting MediConnect database seeding...'))

        # Create or retrieve Demo Patient
        patient_email = 'patient@mediconnect.com'
        patient_user, created = User.objects.get_or_create(
            email=patient_email,
            defaults={
                'username': patient_email,
                'full_name': 'Rahul Sharma',
                'role': 'PATIENT',
                'phone': '+91 98765 43210',
                'is_active': True,
                'is_deleted': False
            }
        )
        patient_user.set_password('Password123!')
        patient_user.save()

        PatientProfile.objects.get_or_create(
            user=patient_user,
            defaults={
                'date_of_birth': date(1994, 5, 14),
                'gender': 'Male',
                'blood_group': 'O+',
                'address': 'Flat 402, Green View Apts, Koramangala, Bangalore',
                'emergency_contact': '+91 98765 99999 (Anita Sharma - Spouse)',
                'medical_history': 'Mild seasonal allergies, controlled hypertension.'
            }
        )
        self.stdout.write(self.style.SUCCESS(f'Demo patient ready: {patient_email} / Password123!'))

        # 5 Sample Doctors Data
        sample_doctors = [
            {
                'email': 'dr.arun@mediconnect.com',
                'full_name': 'Dr. Arun Kumar',
                'specialization': 'Cardiologist',
                'qualifications': 'MBBS, MD (Cardiology), FACC',
                'experience_years': 8,
                'hospital_name': 'City Hospital',
                'location': 'Bangalore, Indiranagar',
                'consultation_fee': 800.00,
                'rating': 4.9,
                'total_reviews': 142,
                'bio': 'Specialist in non-invasive cardiology, preventive cardiac care, and hypertension management. Dedicated to early detection and evidence-based personalized cardiovascular therapies.',
                'profile_image': 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&w=600&q=80',
                'phone': '+91 98450 11223'
            },
            {
                'email': 'dr.priya@mediconnect.com',
                'full_name': 'Dr. Priya Sharma',
                'specialization': 'Dermatologist',
                'qualifications': 'MBBS, MD (Dermatology & Venereology)',
                'experience_years': 6,
                'hospital_name': 'Apollo Clinic',
                'location': 'Bangalore, Koramangala',
                'consultation_fee': 650.00,
                'rating': 4.8,
                'total_reviews': 98,
                'bio': 'Expert dermatologist focusing on medical dermatology, acne treatment, chronic eczema, cosmetic care, and skin allergies with comprehensive patient guidance.',
                'profile_image': 'https://images.unsplash.com/photo-1594824813572-c20e29b16521?auto=format&fit=crop&w=600&q=80',
                'phone': '+91 98450 22334'
            },
            {
                'email': 'dr.rohan@mediconnect.com',
                'full_name': 'Dr. Rohan Mehta',
                'specialization': 'Neurologist',
                'qualifications': 'MBBS, MD, DM (Neurology)',
                'experience_years': 10,
                'hospital_name': 'Fortis Hospital',
                'location': 'Bangalore, Bannerghatta Road',
                'consultation_fee': 1000.00,
                'rating': 4.9,
                'total_reviews': 210,
                'bio': 'Renowned clinical neurologist with over a decade of clinical experience in stroke rehabilitation, migraine therapeutics, epilepsy management, and neuropathy care.',
                'profile_image': 'https://images.unsplash.com/photo-1537368910025-700350fe46c7?auto=format&fit=crop&w=600&q=80',
                'phone': '+91 98450 33445'
            },
            {
                'email': 'dr.sneha@mediconnect.com',
                'full_name': 'Dr. Sneha Patel',
                'specialization': 'Pediatrician',
                'qualifications': 'MBBS, MD (Pediatrics), DCH',
                'experience_years': 7,
                'hospital_name': 'Rainbow Children\'s Hospital',
                'location': 'Bangalore, Marathahalli',
                'consultation_fee': 600.00,
                'rating': 4.9,
                'total_reviews': 165,
                'bio': 'Compassionate child health specialist committed to newborn care, child immunization schedules, developmental milestones, and pediatric nutrition guidance.',
                'profile_image': 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=600&q=80',
                'phone': '+91 98450 44556'
            },
            {
                'email': 'dr.vikram@mediconnect.com',
                'full_name': 'Dr. Vikram Rao',
                'specialization': 'General Physician',
                'qualifications': 'MBBS',
                'experience_years': 5,
                'hospital_name': 'Manipal Hospital',
                'location': 'Bangalore, Whitefield',
                'consultation_fee': 500.00,
                'rating': 4.7,
                'total_reviews': 89,
                'bio': 'Primary care physician providing holistic medical evaluations, lifestyle guidance, chronic disease monitoring, fever workups, and health checkups.',
                'profile_image': 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=600&q=80',
                'phone': '+91 98450 55667'
            }
        ]

        created_doctor_profiles = []

        for doc in sample_doctors:
            doc_user, _ = User.objects.get_or_create(
                email=doc['email'],
                defaults={
                    'username': doc['email'],
                    'full_name': doc['full_name'],
                    'role': 'DOCTOR',
                    'phone': doc['phone'],
                    'is_active': True,
                    'is_deleted': False
                }
            )
            doc_user.set_password('Doctor123!')
            doc_user.save()

            doctor_profile, _ = DoctorProfile.objects.update_or_create(
                user=doc_user,
                defaults={
                    'specialization': doc['specialization'],
                    'qualifications': doc['qualifications'],
                    'experience_years': doc['experience_years'],
                    'hospital_name': doc['hospital_name'],
                    'location': doc['location'],
                    'consultation_fee': doc['consultation_fee'],
                    'rating': doc['rating'],
                    'total_reviews': doc['total_reviews'],
                    'bio': doc['bio'],
                    'profile_image': doc['profile_image'],
                    'is_available': True
                }
            )
            created_doctor_profiles.append(doctor_profile)
            self.stdout.write(self.style.SUCCESS(f"Seeded: {doc['full_name']} ({doc['specialization']})"))

        # Seed appointment slots for the next 7 days for all 5 doctors
        today = timezone.localdate()
        daily_time_slots = [
            (time(9, 0), time(9, 30)),
            (time(9, 30), time(10, 0)),
            (time(10, 30), time(11, 0)),
            (time(11, 0), time(11, 30)),
            (time(14, 0), time(14, 30)),
            (time(15, 0), time(15, 30)),
            (time(16, 0), time(16, 30)),
        ]

        slot_count = 0
        for doctor in created_doctor_profiles:
            for day_offset in range(1, 8):
                slot_date = today + timedelta(days=day_offset)
                for start_t, end_t in daily_time_slots:
                    slot, created_slot = AppointmentSlot.objects.get_or_create(
                        doctor=doctor,
                        date=slot_date,
                        start_time=start_t,
                        defaults={
                            'end_time': end_t,
                            'duration_minutes': 30,
                            'consultation_fee': doctor.consultation_fee,
                            'is_booked': False,
                            'is_active': True
                        }
                    )
                    if created_slot:
                        slot_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {slot_count} available appointment slots.'))

        # Seed realistic demonstration appointments and prescriptions
        dr_arun = created_doctor_profiles[0]
        dr_priya = created_doctor_profiles[1]

        # 1. Completed appointment with prescription for Dr. Arun Kumar
        past_date = today - timedelta(days=3)
        past_slot, _ = AppointmentSlot.objects.get_or_create(
            doctor=dr_arun,
            date=past_date,
            start_time=time(10, 0),
            defaults={
                'end_time': time(10, 30),
                'duration_minutes': 30,
                'consultation_fee': dr_arun.consultation_fee,
                'is_booked': True,
                'is_active': True
            }
        )
        past_slot.is_booked = True
        past_slot.save()

        completed_booking, _ = AppointmentBooking.objects.get_or_create(
            slot=past_slot,
            defaults={
                'patient': patient_user,
                'doctor': dr_arun,
                'status': 'COMPLETED',
                'patient_notes': 'Experiencing occasional mild chest tightness after brisk walking.',
                'doctor_notes': 'ECG normal, blood pressure slightly elevated (138/88). Advised routine lipid profile test and mild cardio exercises.'
            }
        )

        # Create Prescription for this completed booking
        prescription, _ = Prescription.objects.get_or_create(
            appointment=completed_booking,
            defaults={
                'patient': patient_user,
                'doctor': dr_arun,
                'diagnosis': 'Stage 1 Hypertension & Mild Exertional Fatigue',
                'notes': 'Reduce dietary sodium intake. Walk for 30 minutes daily. Follow up in 3 weeks with fresh lipid profile.'
            }
        )

        PrescriptionItem.objects.get_or_create(
            prescription=prescription,
            medicine_name='Telmisartan',
            defaults={
                'dosage': '40 mg',
                'frequency': 'Once daily (Morning after breakfast)',
                'duration': '30 days',
                'instructions': 'Take with a full glass of water. Monitor morning BP twice weekly.'
            }
        )
        PrescriptionItem.objects.get_or_create(
            prescription=prescription,
            medicine_name='Coenzyme Q10 + Omega-3',
            defaults={
                'dosage': '100 mg / 1000 mg',
                'frequency': 'Once daily with dinner',
                'duration': '30 days',
                'instructions': 'Dietary cardiac supplement.'
            }
        )

        # 2. Upcoming accepted booking with Dr. Priya Sharma
        upcoming_date = today + timedelta(days=2)
        upcoming_slot, _ = AppointmentSlot.objects.get_or_create(
            doctor=dr_priya,
            date=upcoming_date,
            start_time=time(11, 0),
            defaults={
                'end_time': time(11, 30),
                'duration_minutes': 30,
                'consultation_fee': dr_priya.consultation_fee,
                'is_booked': True,
                'is_active': True
            }
        )
        upcoming_slot.is_booked = True
        upcoming_slot.save()

        AppointmentBooking.objects.get_or_create(
            slot=upcoming_slot,
            defaults={
                'patient': patient_user,
                'doctor': dr_priya,
                'status': 'ACCEPTED',
                'patient_notes': 'Skin redness and dry rash on forearm appearing after outdoor gardening.',
                'doctor_notes': 'Scheduled consultation. Patient requested topical patch review.'
            }
        )

        # 3. Pending booking with Dr. Sneha Patel
        pending_date = today + timedelta(days=4)
        pending_slot, _ = AppointmentSlot.objects.get_or_create(
            doctor=created_doctor_profiles[3],
            date=pending_date,
            start_time=time(14, 0),
            defaults={
                'end_time': time(14, 30),
                'duration_minutes': 30,
                'consultation_fee': created_doctor_profiles[3].consultation_fee,
                'is_booked': True,
                'is_active': True
            }
        )
        pending_slot.is_booked = True
        pending_slot.save()

        AppointmentBooking.objects.get_or_create(
            slot=pending_slot,
            defaults={
                'patient': patient_user,
                'doctor': created_doctor_profiles[3],
                'status': 'PENDING',
                'patient_notes': 'Routine child growth checkup and pending MMR vaccination inquiry.',
                'doctor_notes': ''
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded MediConnect with all 5 sample doctors, slots, and demo appointments!'))
