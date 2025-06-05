# BE/shared/management/commands/initialize_healthcare_system.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import uuid

# Import all models.py
from shared.models import User, Doctor, Patient, Nurse
from laboratory.models import Laboratory, LabTest, LabOrder, LabResult
from pharmacy.models import Pharmacy, Medication, PharmacyInventory, Prescription
from finance.models import Insurance, Invoice, InvoiceItem, Payment
from records.models import HealthRecord, VitalSigns, MedicalHistory, Allergy
from notifications.models import NotificationTemplate, NotificationPreference

class Command(BaseCommand):
    help = 'Initialize the healthcare system with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip creating sample users',
        )
        parser.add_argument(
            '--skip-medical',
            action='store_true',
            help='Skip creating medical data',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing data first',
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('Cleaning existing data...')
            self.clean_data()

        self.stdout.write('Initializing Healthcare System...')

        if not options['skip_users']:
            self.create_sample_users()

        self.create_laboratories()
        self.create_pharmacies()
        self.create_notification_templates()

        if not options['skip_medical']:
            self.create_sample_medical_data()

        self.stdout.write(
            self.style.SUCCESS('Successfully initialized healthcare system!')
        )

    def clean_data(self):
        """Clean existing data"""
        models_to_clean = [
            LabResult, LabOrder, LabTest, Laboratory,
            Prescription, PharmacyInventory, Medication, Pharmacy,
            Payment, InvoiceItem, Invoice, Insurance,
            VitalSigns, MedicalHistory, Allergy, HealthRecord,
            NotificationPreference, NotificationTemplate,
            Nurse, Patient, Doctor, User
        ]

        for model in models_to_clean:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'Deleted {count} {model.__name__} records')

    def create_sample_users(self):
        """Create sample users"""
        self.stdout.write('Creating sample users...')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@healthcare.com',
                password='admin123',
                first_name='System',
                last_name='Administrator'
            )
            self.stdout.write(f'Created admin user: {admin.username}')

        # Create sample doctors
        doctors_data = [
            {
                'username': 'dr_smith',
                'email': 'dr.smith@healthcare.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'specialization': 'Cardiology',
                'phone_number': '555-0101'
            },
            {
                'username': 'dr_johnson',
                'email': 'dr.johnson@healthcare.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'specialization': 'Pediatrics',
                'phone_number': '555-0102'
            },
            {
                'username': 'dr_wilson',
                'email': 'dr.wilson@healthcare.com',
                'first_name': 'Michael',
                'last_name': 'Wilson',
                'specialization': 'Orthopedics',
                'phone_number': '555-0103'
            }
        ]

        for doctor_data in doctors_data:
            if not User.objects.filter(username=doctor_data['username']).exists():
                user = User.objects.create_user(
                    username=doctor_data['username'],
                    email=doctor_data['email'],
                    password='doctor123',
                    first_name=doctor_data['first_name'],
                    last_name=doctor_data['last_name'],
                    phone_number=doctor_data['phone_number'],
                    is_doctor=True
                )
                Doctor.objects.create(
                    user=user,
                    specialization=doctor_data['specialization']
                )
                self.stdout.write(f'Created doctor: Dr. {user.get_full_name()}')

        # Create sample patients
        patients_data = [
            {
                'username': 'patient1',
                'email': 'patient1@email.com',
                'first_name': 'Alice',
                'last_name': 'Brown',
                'phone_number': '555-0201',
                'date_of_birth': date(1990, 5, 15)
            },
            {
                'username': 'patient2',
                'email': 'patient2@email.com',
                'first_name': 'Bob',
                'last_name': 'Davis',
                'phone_number': '555-0202',
                'date_of_birth': date(1985, 8, 22)
            },
            {
                'username': 'patient3',
                'email': 'patient3@email.com',
                'first_name': 'Carol',
                'last_name': 'Miller',
                'phone_number': '555-0203',
                'date_of_birth': date(1992, 12, 8)
            }
        ]

        for patient_data in patients_data:
            if not User.objects.filter(username=patient_data['username']).exists():
                user = User.objects.create_user(
                    username=patient_data['username'],
                    email=patient_data['email'],
                    password='patient123',
                    first_name=patient_data['first_name'],
                    last_name=patient_data['last_name'],
                    phone_number=patient_data['phone_number'],
                    is_patient=True
                )
                Patient.objects.create(
                    user=user,
                    date_of_birth=patient_data['date_of_birth']
                )
                self.stdout.write(f'Created patient: {user.get_full_name()}')

        # Create sample nurses
        nurses_data = [
            {
                'username': 'nurse_mary',
                'email': 'nurse.mary@healthcare.com',
                'first_name': 'Mary',
                'last_name': 'Jones',
                'phone_number': '555-0301',
                'qualification': 'RN',
                'department': 'ICU',
                'license_number': 'RN123456'
            },
            {
                'username': 'nurse_james',
                'email': 'nurse.james@healthcare.com',
                'first_name': 'James',
                'last_name': 'Wilson',
                'phone_number': '555-0302',
                'qualification': 'LPN',
                'department': 'Emergency',
                'license_number': 'LPN123456'
            }
        ]

        for nurse_data in nurses_data:
            if not User.objects.filter(username=nurse_data['username']).exists():
                user = User.objects.create_user(
                    username=nurse_data['username'],
                    email=nurse_data['email'],
                    password='nurse123',
                    first_name=nurse_data['first_name'],
                    last_name=nurse_data['last_name'],
                    phone_number=nurse_data['phone_number']
                )
                Nurse.objects.create(
                    user=user,
                    qualification=nurse_data['qualification'],
                    department=nurse_data['department'],
                    license_number=nurse_data['license_number'],
                    hire_date=date.today() - timedelta(days=365)
                )
                self.stdout.write(f'Created nurse: {user.get_full_name()}')

    def create_laboratories(self):
        """Create sample laboratories and tests"""
        self.stdout.write('Creating laboratories...')

        # Create laboratories
        labs_data = [
            {
                'name': 'Central Pathology Lab',
                'lab_type': 'PATHOLOGY',
                'location': 'Building A, Floor 2',
                'phone_number': '555-1001',
                'email': 'pathology@healthcare.com',
                'operating_hours': 'Mon-Fri: 7AM-7PM, Sat: 8AM-4PM'
            },
            {
                'name': 'Radiology Department',
                'lab_type': 'RADIOLOGY',
                'location': 'Building B, Floor 1',
                'phone_number': '555-1002',
                'email': 'radiology@healthcare.com',
                'operating_hours': '24/7 Emergency, Regular: Mon-Fri 6AM-10PM'
            }
        ]

        for lab_data in labs_data:
            lab, created = Laboratory.objects.get_or_create(
                name=lab_data['name'],
                defaults=lab_data
            )
            if created:
                self.stdout.write(f'Created laboratory: {lab.name}')

        # Create lab tests
        pathology_lab = Laboratory.objects.get(name='Central Pathology Lab')
        tests_data = [
            {
                'name': 'Complete Blood Count',
                'code': 'CBC',
                'category': 'BLOOD',
                'description': 'Comprehensive blood analysis including RBC, WBC, platelets',
                'normal_range': 'Varies by component',
                'sample_type': 'Blood',
                'cost': Decimal('45.00'),
                'duration_hours': 4,
                'laboratory': pathology_lab
            },
            {
                'name': 'Lipid Panel',
                'code': 'LIPID',
                'category': 'BLOOD',
                'description': 'Cholesterol and triglyceride levels',
                'normal_range': 'Total cholesterol < 200 mg/dL',
                'sample_type': 'Blood serum',
                'cost': Decimal('35.00'),
                'duration_hours': 6,
                'laboratory': pathology_lab,
                'preparation_instructions': 'Fast for 12 hours before test'
            }
        ]

        for test_data in tests_data:
            test, created = LabTest.objects.get_or_create(
                code=test_data['code'],
                defaults=test_data
            )
            if created:
                self.stdout.write(f'Created lab test: {test.name}')

    def create_pharmacies(self):
        """Create sample pharmacies and medications"""
        self.stdout.write('Creating pharmacies...')

        # Create pharmacy
        pharmacy_data = {
            'name': 'HealthCare Main Pharmacy',
            'pharmacy_type': 'HOSPITAL',
            'license_number': 'PH123456789',
            'address': '123 Medical Center Dr, Healthcare City, HC 12345',
            'phone_number': '555-2001',
            'email': 'pharmacy@healthcare.com',
            'operating_hours': 'Mon-Fri: 7AM-9PM, Sat-Sun: 9AM-6PM',
            'is_24_hours': False,
            'delivery_available': True
        }

        pharmacy, created = Pharmacy.objects.get_or_create(
            name=pharmacy_data['name'],
            defaults=pharmacy_data
        )
        if created:
            self.stdout.write(f'Created pharmacy: {pharmacy.name}')

        # Create medications
        medications_data = [
            {
                'name': 'Amoxicillin',
                'generic_name': 'Amoxicillin',
                'brand_name': 'Amoxil',
                'drug_code': 'AMX500',
                'drug_type': 'CAPSULE',
                'category': 'ANTIBIOTIC',
                'strength': '500mg',
                'manufacturer': 'Generic Pharma',
                'description': 'Broad-spectrum antibiotic',
                'side_effects': 'Nausea, diarrhea, rash',
                'contraindications': 'Penicillin allergy',
                'storage_conditions': 'Store at room temperature',
                'unit_price': Decimal('0.50')
            },
            {
                'name': 'Ibuprofen',
                'generic_name': 'Ibuprofen',
                'brand_name': 'Advil',
                'drug_code': 'IBU200',
                'drug_type': 'TABLET',
                'category': 'PAINKILLER',
                'strength': '200mg',
                'manufacturer': 'Pain Relief Corp',
                'description': 'Non-steroidal anti-inflammatory drug',
                'side_effects': 'Stomach upset, dizziness',
                'contraindications': 'Stomach ulcers, kidney disease',
                'storage_conditions': 'Store in dry place',
                'requires_prescription': False,
                'unit_price': Decimal('0.25')
            }
        ]

        for med_data in medications_data:
            medication, created = Medication.objects.get_or_create(
                drug_code=med_data['drug_code'],
                defaults=med_data
            )
            if created:
                self.stdout.write(f'Created medication: {medication.name}')

                # Create inventory for this medication
                PharmacyInventory.objects.create(
                    pharmacy=pharmacy,
                    medication=medication,
                    quantity_in_stock=1000,
                    minimum_stock_level=100,
                    batch_number=f'BATCH{medication.drug_code}001',
                    expiration_date=date.today() + timedelta(days=730),  # 2 years
                    unit_cost=medication.unit_price * Decimal('0.8'),
                    selling_price=medication.unit_price,
                    supplier='Medical Supplies Inc.'
                )

    def create_notification_templates(self):
        """Create notification templates"""
        self.stdout.write('Creating notification templates...')

        templates_data = [
            {
                'name': 'Appointment Reminder',
                'template_type': 'APPOINTMENT_REMINDER',
                'notification_type': 'APPOINTMENT',
                'priority': 'NORMAL',
                'title_template': 'Appointment Reminder - {doctor_name}',
                'message_template': 'You have an appointment with {doctor_name} on {date} at {time}. Please arrive 15 minutes early.',
                'action_text': 'View Appointment',
                'action_url_template': '/my-appointments/{appointment_id}',
                'delivery_methods': ['IN_APP', 'EMAIL', 'SMS'],
                'available_variables': ['doctor_name', 'date', 'time', 'appointment_id', 'location']
            },
            {
                'name': 'Lab Results Ready',
                'template_type': 'LAB_RESULT_READY',
                'notification_type': 'LAB_RESULT',
                'priority': 'HIGH',
                'title_template': 'Your {test_name} Results Are Ready',
                'message_template': 'Your {test_name} results from {date} are now available. Please review them in your patient portal.',
                'action_text': 'View Results',
                'action_url_template': '/lab-results/{result_id}',
                'delivery_methods': ['IN_APP', 'EMAIL'],
                'available_variables': ['test_name', 'date', 'result_id', 'doctor_name']
            },
            {
                'name': 'Prescription Ready',
                'template_type': 'PRESCRIPTION_READY',
                'notification_type': 'PRESCRIPTION',
                'priority': 'NORMAL',
                'title_template': 'Prescription Ready for Pickup',
                'message_template': 'Your prescription for {medication_name} is ready for pickup at {pharmacy_name}.',
                'action_text': 'View Details',
                'action_url_template': '/prescriptions/{prescription_id}',
                'delivery_methods': ['IN_APP', 'SMS'],
                'available_variables': ['medication_name', 'pharmacy_name', 'prescription_id', 'pickup_location']
            }
        ]

        for template_data in templates_data:
            template, created = NotificationTemplate.objects.get_or_create(
                template_type=template_data['template_type'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'Created notification template: {template.name}')

    def create_sample_medical_data(self):
        """Create sample medical data"""
        self.stdout.write('Creating sample medical data...')

        # Get sample users
        try:
            patient = Patient.objects.first()
            doctor = Doctor.objects.first()

            if not patient or not doctor:
                self.stdout.write('No patients or doctors found. Skipping medical data creation.')
                return

            # Create health record
            health_record = HealthRecord.objects.create(
                record_id=f'HR{uuid.uuid4().hex[:8].upper()}',
                patient=patient,
                doctor=doctor,
                record_type='CONSULTATION',
                title='Annual Physical Examination',
                description='Routine annual physical examination and health assessment',
                chief_complaint='Annual checkup',
                diagnosis='Patient appears healthy, no acute issues identified',
                treatment_plan='Continue current lifestyle, follow-up in 1 year',
                service_date=date.today(),
                created_by=doctor.user,
                last_modified_by=doctor.user
            )

            # Create vital signs
            VitalSigns.objects.create(
                health_record=health_record,
                patient=patient,
                systolic_bp=120,
                diastolic_bp=80,
                heart_rate=72,
                respiratory_rate=16,
                temperature=Decimal('98.6'),
                oxygen_saturation=98,
                height_cm=170,
                weight_kg=Decimal('70.5'),
                measured_by=doctor.user
            )

            # Create medical history
            MedicalHistory.objects.create(
                patient=patient,
                condition_name='Hypertension',
                icd_code='I10',
                status='ACTIVE',
                diagnosed_date=date.today() - timedelta(days=365),
                severity='Mild',
                notes='Well controlled with medication',
                doctor=doctor
            )

            # Create allergy
            Allergy.objects.create(
                patient=patient,
                allergen_name='Penicillin',
                allergen_type='MEDICATION',
                severity='MODERATE',
                reaction_description='Skin rash and itching',
                symptoms='Red rash, itching, mild swelling',
                first_occurrence_date=date.today() - timedelta(days=1000),
                reported_by=doctor.user
            )

            # Create insurance
            Insurance.objects.create(
                company_name='HealthFirst Insurance',
                policy_number='HF123456789',
                patient=patient,
                insurance_type='HEALTH',
                coverage_type='INDIVIDUAL',
                subscriber_name=patient.user.get_full_name(),
                subscriber_id='SUB123456',
                relationship_to_patient='Self',
                effective_date=date.today() - timedelta(days=180),
                expiration_date=date.today() + timedelta(days=185),
                copay_amount=Decimal('25.00'),
                deductible_amount=Decimal('1000.00'),
                out_of_pocket_max=Decimal('5000.00'),
                contact_phone='1-800-HEALTH1',
                contact_email='support@healthfirst.com'
            )

            self.stdout.write('Created sample medical data')

        except Exception as e:
            self.stdout.write(f'Error creating medical data: {e}')

    def create_notification_preferences(self):
        """Create default notification preferences for all users"""
        self.stdout.write('Creating notification preferences...')

        for user in User.objects.all():
            NotificationPreference.objects.get_or_create(
                user=user,
                defaults={
                    'appointment_reminders': True,
                    'appointment_confirmations': True,
                    'appointment_cancellations': True,
                    'lab_results': True,
                    'prescription_ready': True,
                    'medication_reminders': True,
                    'billing_notifications': True,
                    'payment_confirmations': True,
                    'system_updates': True,
                    'security_alerts': True,
                }
            )
        self.stdout.write('Created notification preferences for all users')