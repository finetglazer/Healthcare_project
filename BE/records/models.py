# BE/records/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class HealthRecord(models.Model):
    RECORD_TYPE_CHOICES = [
        ('CONSULTATION', 'Consultation'),
        ('DIAGNOSIS', 'Diagnosis'),
        ('TREATMENT', 'Treatment'),
        ('SURGERY', 'Surgery'),
        ('LAB_RESULT', 'Laboratory Result'),
        ('IMAGING', 'Medical Imaging'),
        ('VACCINATION', 'Vaccination'),
        ('ALLERGY', 'Allergy Record'),
        ('MEDICATION', 'Medication Record'),
        ('VITAL_SIGNS', 'Vital Signs'),
        ('EMERGENCY', 'Emergency Visit'),
        ('DISCHARGE', 'Discharge Summary'),
    ]

    PRIVACY_LEVEL_CHOICES = [
        ('PUBLIC', 'Public'),
        ('RESTRICTED', 'Restricted'),
        ('CONFIDENTIAL', 'Confidential'),
        ('SECRET', 'Secret'),
    ]

    record_id = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE, related_name='health_records')
    doctor = models.ForeignKey('shared.Doctor', on_delete=models.CASCADE, related_name='created_records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    clinical_notes = models.TextField(blank=True)

    # Medical Details
    chief_complaint = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_instructions = models.TextField(blank=True)

    # Privacy and Access
    privacy_level = models.CharField(max_length=20, choices=PRIVACY_LEVEL_CHOICES, default='RESTRICTED')
    authorized_users = models.ManyToManyField('shared.User', blank=True, related_name='authorized_records')

    # Dates and Tracking
    service_date = models.DateField()
    created_by = models.ForeignKey('shared.User', on_delete=models.CASCADE, related_name='created_health_records')
    last_modified_by = models.ForeignKey('shared.User', on_delete=models.CASCADE, related_name='modified_health_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Digital signature and verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey('shared.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_records')
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.record_type} - {self.patient.user.get_full_name()} - {self.service_date}"

    class Meta:
        db_table = 'health_records'
        ordering = ['-service_date', '-created_at']

class VitalSigns(models.Model):
    health_record = models.OneToOneField(HealthRecord, on_delete=models.CASCADE, related_name='vital_signs')
    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE, related_name='vital_signs')

    # Basic Vitals
    systolic_bp = models.PositiveIntegerField(
        validators=[MinValueValidator(60), MaxValueValidator(300)],
        help_text="Systolic Blood Pressure (mmHg)"
    )
    diastolic_bp = models.PositiveIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        help_text="Diastolic Blood Pressure (mmHg)"
    )
    heart_rate = models.PositiveIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(250)],
        help_text="Heart Rate (beats per minute)"
    )
    respiratory_rate = models.PositiveIntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(60)],
        help_text="Respiratory Rate (breaths per minute)"
    )
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1,
        validators=[MinValueValidator(90.0), MaxValueValidator(115.0)],
        help_text="Body Temperature (°F)"
    )
    oxygen_saturation = models.PositiveIntegerField(
        validators=[MinValueValidator(70), MaxValueValidator(100)],
        help_text="Oxygen Saturation (%)"
    )

    # Additional Measurements
    height_cm = models.PositiveIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(300)],
        null=True, blank=True,
        help_text="Height in centimeters"
    )
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(1.0), MaxValueValidator(500.0)],
        null=True, blank=True,
        help_text="Weight in kilograms"
    )
    bmi = models.DecimalField(
        max_digits=4, decimal_places=1,
        null=True, blank=True,
        help_text="Body Mass Index (calculated)"
    )
    blood_glucose = models.PositiveIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(800)],
        null=True, blank=True,
        help_text="Blood Glucose (mg/dL)"
    )

    # Assessment
    pain_scale = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Pain Scale (0-10)"
    )

    # Metadata
    measured_by = models.ForeignKey('shared.User', on_delete=models.CASCADE, related_name='measured_vitals')
    measured_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Calculate BMI if height and weight are provided
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            self.bmi = round(float(self.weight_kg) / (height_m ** 2), 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Vitals for {self.patient.user.get_full_name()} - {self.measured_at.date()}"

    class Meta:
        db_table = 'vital_signs'
        ordering = ['-measured_at']

class MedicalHistory(models.Model):
    CONDITION_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RESOLVED', 'Resolved'),
        ('CHRONIC', 'Chronic'),
        ('FAMILY_HISTORY', 'Family History'),
    ]

    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE, related_name='medical_history')
    condition_name = models.CharField(max_length=200)
    icd_code = models.CharField(max_length=20, blank=True, help_text="ICD-10 Code")
    status = models.CharField(max_length=20, choices=CONDITION_STATUS_CHOICES)
    diagnosed_date = models.DateField(null=True, blank=True)
    resolved_date = models.DateField(null=True, blank=True)
    severity = models.CharField(max_length=50, blank=True)  # Mild, Moderate, Severe
    notes = models.TextField(blank=True)
    family_relation = models.CharField(max_length=100, blank=True)  # For family history
    doctor = models.ForeignKey('shared.Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.condition_name} - {self.patient.user.get_full_name()}"

    class Meta:
        db_table = 'medical_history'
        ordering = ['-diagnosed_date']

class Allergy(models.Model):
    SEVERITY_CHOICES = [
        ('MILD', 'Mild'),
        ('MODERATE', 'Moderate'),
        ('SEVERE', 'Severe'),
        ('LIFE_THREATENING', 'Life Threatening'),
    ]

    ALLERGEN_TYPE_CHOICES = [
        ('MEDICATION', 'Medication'),
        ('FOOD', 'Food'),
        ('ENVIRONMENTAL', 'Environmental'),
        ('LATEX', 'Latex'),
        ('INSECT', 'Insect'),
        ('OTHER', 'Other'),
    ]

    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE, related_name='allergies')
    allergen_name = models.CharField(max_length=200)
    allergen_type = models.CharField(max_length=20, choices=ALLERGEN_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    reaction_description = models.TextField()
    symptoms = models.TextField(blank=True)
    treatment_notes = models.TextField(blank=True)
    first_occurrence_date = models.DateField(null=True, blank=True)
    last_occurrence_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    reported_by = models.ForeignKey('shared.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.allergen_name} - {self.patient.user.get_full_name()}"

    class Meta:
        db_table = 'allergies'
        ordering = ['-severity', 'allergen_name']