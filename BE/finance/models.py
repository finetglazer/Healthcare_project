# BE/finance/models.py
from django.db import models
from decimal import Decimal

class Insurance(models.Model):
    INSURANCE_TYPE_CHOICES = [
        ('HEALTH', 'Health Insurance'),
        ('DENTAL', 'Dental Insurance'),
        ('VISION', 'Vision Insurance'),
        ('LIFE', 'Life Insurance'),
        ('DISABILITY', 'Disability Insurance'),
    ]

    COVERAGE_TYPE_CHOICES = [
        ('INDIVIDUAL', 'Individual'),
        ('FAMILY', 'Family'),
        ('GROUP', 'Group'),
        ('GOVERNMENT', 'Government'),
    ]

    company_name = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=100, unique=True)
    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE, related_name='insurances')
    insurance_type = models.CharField(max_length=20, choices=INSURANCE_TYPE_CHOICES)
    coverage_type = models.CharField(max_length=20, choices=COVERAGE_TYPE_CHOICES)
    group_number = models.CharField(max_length=100, blank=True)
    subscriber_name = models.CharField(max_length=200)
    subscriber_id = models.CharField(max_length=100)
    relationship_to_patient = models.CharField(max_length=50)  # Self, Spouse, Child, etc.
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    copay_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductible_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    out_of_pocket_max = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coverage_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=80.00)  # 80%
    is_primary = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.policy_number}"

    class Meta:
        db_table = 'insurances'

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    INVOICE_TYPE_CHOICES = [
        ('CONSULTATION', 'Consultation'),
        ('PROCEDURE', 'Medical Procedure'),
        ('LAB_TEST', 'Laboratory Test'),
        ('MEDICATION', 'Medication'),
        ('SURGERY', 'Surgery'),
        ('EMERGENCY', 'Emergency Service'),
        ('ROOM_CHARGE', 'Room Charge'),
        ('OTHER', 'Other'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE, related_name='invoices')
    doctor = models.ForeignKey('shared.Doctor', on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)

    # Financial Details
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Insurance
    insurance_claim_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patient_responsibility = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    description = models.TextField()
    notes = models.TextField(blank=True)

    # Dates
    service_date = models.DateField()
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - ${self.total_amount}"

    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status not in ['PAID', 'CANCELLED']

    class Meta:
        db_table = 'invoices'

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    service_code = models.CharField(max_length=50, blank=True)  # CPT code, etc.
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - ${self.total_price}"

    class Meta:
        db_table = 'invoice_items'

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHECK', 'Check'),
        ('INSURANCE', 'Insurance'),
        ('MOBILE_PAYMENT', 'Mobile Payment'),
        ('CRYPTOCURRENCY', 'Cryptocurrency'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    payment_id = models.CharField(max_length=50, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')

    # Payment Details
    transaction_id = models.CharField(max_length=200, blank=True)  # From payment processor
    reference_number = models.CharField(max_length=100, blank=True)
    card_last_four = models.CharField(max_length=4, blank=True)  # Last 4 digits of card

    # Insurance Payment Details
    insurance = models.ForeignKey(Insurance, on_delete=models.SET_NULL, null=True, blank=True)
    claim_number = models.CharField(max_length=100, blank=True)

    # Processing Details
    processed_by = models.ForeignKey('shared.User', on_delete=models.SET_NULL, null=True, blank=True)
    processor_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payment {self.payment_id} - ${self.amount}"

    class Meta:
        db_table = 'payments'

class Refund(models.Model):
    REFUND_STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]

    refund_id = models.CharField(max_length=50, unique=True)
    original_payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='REQUESTED')
    requested_by = models.ForeignKey('shared.User', on_delete=models.CASCADE, related_name='requested_refunds')
    approved_by = models.ForeignKey('shared.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_refunds')
    processed_by = models.ForeignKey('shared.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    transaction_id = models.CharField(max_length=200, blank=True)
    requested_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Refund {self.refund_id} - ${self.amount}"

    class Meta:
        db_table = 'refunds'