# BE/pharmacy/models.py
from django.db import models
from decimal import Decimal

class Pharmacy(models.Model):
    PHARMACY_TYPE_CHOICES = [
        ('HOSPITAL', 'Hospital Pharmacy'),
        ('RETAIL', 'Retail Pharmacy'),
        ('CLINICAL', 'Clinical Pharmacy'),
        ('ONLINE', 'Online Pharmacy'),
    ]

    name = models.CharField(max_length=200)
    pharmacy_type = models.CharField(max_length=20, choices=PHARMACY_TYPE_CHOICES)
    license_number = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    operating_hours = models.CharField(max_length=100)
    is_24_hours = models.BooleanField(default=False)
    delivery_available = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.pharmacy_type}"

    class Meta:
        db_table = 'pharmacies'
        verbose_name_plural = 'Pharmacies'

class Medication(models.Model):
    DRUG_TYPE_CHOICES = [
        ('TABLET', 'Tablet'),
        ('CAPSULE', 'Capsule'),
        ('LIQUID', 'Liquid/Syrup'),
        ('INJECTION', 'Injection'),
        ('CREAM', 'Cream/Ointment'),
        ('INHALER', 'Inhaler'),
        ('DROPS', 'Drops'),
        ('PATCH', 'Patch'),
    ]

    CATEGORY_CHOICES = [
        ('ANTIBIOTIC', 'Antibiotic'),
        ('PAINKILLER', 'Pain Killer'),
        ('ANTIVIRAL', 'Antiviral'),
        ('ANTIFUNGAL', 'Antifungal'),
        ('CARDIAC', 'Cardiac Medicine'),
        ('DIABETES', 'Diabetes Medicine'),
        ('HYPERTENSION', 'Hypertension Medicine'),
        ('RESPIRATORY', 'Respiratory Medicine'),
        ('MENTAL_HEALTH', 'Mental Health Medicine'),
        ('VITAMIN', 'Vitamin/Supplement'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200)
    brand_name = models.CharField(max_length=200, blank=True)
    drug_code = models.CharField(max_length=50, unique=True)  # NDC or similar
    drug_type = models.CharField(max_length=20, choices=DRUG_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    strength = models.CharField(max_length=100)  # "500mg", "10mg/ml"
    manufacturer = models.CharField(max_length=200)
    description = models.TextField()
    side_effects = models.TextField()
    contraindications = models.TextField()
    storage_conditions = models.CharField(max_length=200)
    requires_prescription = models.BooleanField(default=True)
    is_controlled_substance = models.BooleanField(default=False)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.strength}"

    class Meta:
        db_table = 'medications'

class PharmacyInventory(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='inventory')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='inventory')
    quantity_in_stock = models.PositiveIntegerField(default=0)
    minimum_stock_level = models.PositiveIntegerField(default=10)
    batch_number = models.CharField(max_length=100)
    expiration_date = models.DateField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=200)
    last_restocked = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication.name} at {self.pharmacy.name} - Stock: {self.quantity_in_stock}"

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.minimum_stock_level

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expiration_date < timezone.now().date()

    class Meta:
        db_table = 'pharmacy_inventory'
        unique_together = ['pharmacy', 'medication', 'batch_number']

class Prescription(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('FILLED', 'Filled'),
        ('DISPENSED', 'Dispensed'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]

    FREQUENCY_CHOICES = [
        ('ONCE_DAILY', 'Once Daily'),
        ('TWICE_DAILY', 'Twice Daily'),
        ('THREE_TIMES', 'Three Times Daily'),
        ('FOUR_TIMES', 'Four Times Daily'),
        ('AS_NEEDED', 'As Needed'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]

    prescription_number = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey('shared.Doctor', on_delete=models.CASCADE, related_name='prescriptions')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='prescriptions')
    dosage = models.CharField(max_length=100)  # "Take 1 tablet"
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration_days = models.PositiveIntegerField()
    quantity_prescribed = models.PositiveIntegerField()
    refills_allowed = models.PositiveIntegerField(default=0)
    refills_used = models.PositiveIntegerField(default=0)
    instructions = models.TextField()  # "Take with food"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    prescribed_date = models.DateTimeField(auto_now_add=True)
    filled_date = models.DateTimeField(null=True, blank=True)
    dispensed_date = models.DateTimeField(null=True, blank=True)
    expiration_date = models.DateField()
    pharmacist_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Prescription {self.prescription_number} - {self.medication.name}"

    @property
    def can_refill(self):
        return self.refills_used < self.refills_allowed and self.status == 'DISPENSED'

    class Meta:
        db_table = 'prescriptions'