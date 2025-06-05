from django.contrib import admin
from .models import Insurance, Invoice, InvoiceItem, Payment, Refund

@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'policy_number', 'patient', 'insurance_type', 'is_primary', 'is_active']
    list_filter = ['insurance_type', 'coverage_type', 'is_primary', 'is_active']
    search_fields = ['company_name', 'policy_number', 'patient__user__first_name']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient', 'invoice_type', 'total_amount', 'status', 'invoice_date']
    list_filter = ['status', 'invoice_type', 'invoice_date']
    search_fields = ['invoice_number', 'patient__user__first_name', 'patient__user__last_name']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'invoice', 'amount', 'payment_method', 'payment_status', 'payment_date']
    list_filter = ['payment_method', 'payment_status', 'payment_date']
    search_fields = ['payment_id', 'transaction_id']