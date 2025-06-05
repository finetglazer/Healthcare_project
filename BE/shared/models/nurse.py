# BE/shared/models/nurse.py
from django.db import models

class Nurse(models.Model):
    QUALIFICATION_CHOICES = [
        ('RN', 'Registered Nurse'),
        ('LPN', 'Licensed Practical Nurse'),
        ('CNS', 'Clinical Nurse Specialist'),
        ('NP', 'Nurse Practitioner'),
        ('CRNA', 'Certified Registered Nurse Anesthetist'),
        ('CNM', 'Certified Nurse Midwife'),
    ]

    EMPLOYMENT_STATUS_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('TEMP', 'Temporary'),
        ('INACTIVE', 'Inactive'),
    ]

    SHIFT_CHOICES = [
        ('DAY', 'Day Shift'),
        ('NIGHT', 'Night Shift'),
        ('EVENING', 'Evening Shift'),
        ('ROTATING', 'Rotating Shifts'),
        ('ON_CALL', 'On Call'),
    ]

    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='nurse_profile')

    # Professional Information
    qualification = models.CharField(max_length=10, choices=QUALIFICATION_CHOICES)
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True)

    # Employment Details
    employee_id = models.CharField(max_length=20, unique=True)
    hire_date = models.DateField()
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='FULL_TIME')
    shift_preference = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='DAY')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Supervisor
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_nurses')

    # Skills and Certifications
    certifications = models.JSONField(default=list, help_text="List of additional certifications")
    skills = models.JSONField(default=list, help_text="List of nursing skills")

    # Performance and Training
    years_experience = models.PositiveIntegerField(default=0)
    last_training_date = models.DateField(null=True, blank=True)
    performance_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="Rating out of 5.0")

    # Status
    is_active = models.BooleanField(default=True)
    can_supervise = models.BooleanField(default=False)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)

    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.qualification} ({self.department})"

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def is_license_expired(self):
        from django.utils import timezone
        return self.license_expiry < timezone.now().date()

    class Meta:
        db_table = 'nurses'
        ordering = ['user__last_name', 'user__first_name']