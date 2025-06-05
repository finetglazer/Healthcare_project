# BE/laboratory/models.py
from django.db import models
from decimal import Decimal

class Laboratory(models.Model):
    LAB_TYPE_CHOICES = [
        ('PATHOLOGY', 'Pathology Lab'),
        ('RADIOLOGY', 'Radiology'),
        ('MICROBIOLOGY', 'Microbiology'),
        ('BIOCHEMISTRY', 'Biochemistry'),
        ('HEMATOLOGY', 'Hematology'),
        ('IMMUNOLOGY', 'Immunology'),
        ('MOLECULAR', 'Molecular Biology'),
        ('CYTOLOGY', 'Cytology'),
        ('HISTOLOGY', 'Histology'),
    ]

    name = models.CharField(max_length=200)
    lab_type = models.CharField(max_length=20, choices=LAB_TYPE_CHOICES)
    location = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    operating_hours = models.CharField(max_length=200)
    is_24_hours = models.BooleanField(default=False)
    director = models.ForeignKey('shared.Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    accreditation_number = models.CharField(max_length=100, blank=True)
    equipment_list = models.JSONField(default=list, help_text="List of major equipment")
    capacity_per_day = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.lab_type}"

    class Meta:
        db_table = 'laboratories'

class LabTest(models.Model):
    CATEGORY_CHOICES = [
        ('BLOOD', 'Blood Test'),
        ('URINE', 'Urine Test'),
        ('IMAGING', 'Medical Imaging'),
        ('BIOPSY', 'Biopsy'),
        ('CULTURE', 'Culture Test'),
        ('GENETIC', 'Genetic Test'),
        ('HORMONE', 'Hormone Test'),
        ('CARDIAC', 'Cardiac Test'),
        ('LIVER', 'Liver Function'),
        ('KIDNEY', 'Kidney Function'),
        ('LIPID', 'Lipid Profile'),
        ('DIABETES', 'Diabetes Test'),
        ('THYROID', 'Thyroid Function'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)  # CPT code or internal code
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name='tests')
    description = models.TextField()
    normal_range = models.CharField(max_length=200, help_text="Normal values range")
    sample_type = models.CharField(max_length=100, help_text="Blood, Urine, Tissue, etc.")
    sample_volume = models.CharField(max_length=50, blank=True, help_text="Required sample volume")
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    duration_hours = models.PositiveIntegerField(help_text="Time to get results in hours")
    preparation_instructions = models.TextField(blank=True)
    requires_fasting = models.BooleanField(default=False)
    is_urgent_available = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        db_table = 'lab_tests'
        ordering = ['name']

class LabOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COLLECTED', 'Sample Collected'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('ON_HOLD', 'On Hold'),
    ]

    PRIORITY_CHOICES = [
        ('ROUTINE', 'Routine'),
        ('URGENT', 'Urgent'),
        ('STAT', 'STAT (Immediate)'),
        ('EMERGENCY', 'Emergency'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE, related_name='lab_orders')
    doctor = models.ForeignKey('shared.Doctor', on_delete=models.CASCADE, related_name='lab_orders')
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name='orders')
    tests = models.ManyToManyField(LabTest, related_name='orders')

    # Order Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='ROUTINE')
    clinical_notes = models.TextField(blank=True, help_text="Clinical indication for tests")
    special_instructions = models.TextField(blank=True)

    # Sample Information
    sample_collected_at = models.DateTimeField(null=True, blank=True)
    sample_collected_by = models.ForeignKey('shared.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_samples')
    collection_site = models.CharField(max_length=100, blank=True)

    # Timing
    ordered_at = models.DateTimeField(auto_now_add=True)
    expected_completion = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Financial
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_coverage = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patient_responsibility = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Metadata
    created_by = models.ForeignKey('shared.User', on_delete=models.CASCADE, related_name='created_lab_orders')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Lab Order {self.order_number} - {self.patient.user.get_full_name()}"

    @property
    def is_overdue(self):
        if not self.expected_completion:
            return False
        from django.utils import timezone
        return timezone.now() > self.expected_completion and self.status not in ['COMPLETED', 'CANCELLED']

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            import uuid
            self.order_number = f'LAB{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'lab_orders'
        ordering = ['-ordered_at']

class LabResult(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PRELIMINARY', 'Preliminary'),
        ('FINAL', 'Final'),
        ('AMENDED', 'Amended'),
        ('CANCELLED', 'Cancelled'),
    ]

    ABNORMAL_FLAG_CHOICES = [
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('LOW', 'Low'),
        ('CRITICAL_HIGH', 'Critical High'),
        ('CRITICAL_LOW', 'Critical Low'),
        ('ABNORMAL', 'Abnormal'),
    ]

    order = models.ForeignKey(LabOrder, on_delete=models.CASCADE, related_name='results')
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='results')

    # Result Data
    value = models.CharField(max_length=500, help_text="Test result value")
    unit = models.CharField(max_length=50, blank=True, help_text="Unit of measurement")
    reference_range = models.CharField(max_length=200, blank=True)
    abnormal_flag = models.CharField(max_length=20, choices=ABNORMAL_FLAG_CHOICES, default='NORMAL')

    # Status and Verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_critical = models.BooleanField(default=False)
    requires_followup = models.BooleanField(default=False)

    # Personnel
    technician = models.ForeignKey('shared.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_tests')
    verified_by = models.ForeignKey('shared.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_results')

    # Timing
    result_date = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    reported_to_doctor_at = models.DateTimeField(null=True, blank=True)

    # Additional Information
    method = models.CharField(max_length=100, blank=True, help_text="Testing method used")
    equipment_used = models.CharField(max_length=100, blank=True)
    comments = models.TextField(blank=True)
    interpretation = models.TextField(blank=True)

    # Quality Control
    batch_number = models.CharField(max_length=50, blank=True)
    quality_control_passed = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test.name}: {self.value} {self.unit} ({self.abnormal_flag})"

    @property
    def is_abnormal(self):
        return self.abnormal_flag not in ['NORMAL']

    class Meta:
        db_table = 'lab_results'
        ordering = ['-result_date']
        unique_together = ['order', 'test']