from django.contrib import admin
from .models import Pharmacy, Medication, PharmacyInventory, Prescription

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ['name', 'pharmacy_type', 'is_24_hours', 'delivery_available', 'is_active']
    list_filter = ['pharmacy_type', 'is_24_hours', 'delivery_available', 'is_active']
    search_fields = ['name', 'address']

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'drug_type', 'category', 'strength', 'unit_price']
    list_filter = ['drug_type', 'category', 'requires_prescription', 'is_controlled_substance']
    search_fields = ['name', 'generic_name', 'drug_code']

@admin.register(PharmacyInventory)
class PharmacyInventoryAdmin(admin.ModelAdmin):
    list_display = ['medication', 'pharmacy', 'quantity_in_stock', 'is_low_stock', 'expiration_date']
    list_filter = ['pharmacy', 'expiration_date']
    search_fields = ['medication__name', 'batch_number']

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_number', 'patient', 'doctor', 'medication', 'status', 'prescribed_date']
    list_filter = ['status', 'frequency', 'prescribed_date']
    search_fields = ['prescription_number', 'patient__user__first_name', 'patient__user__last_name']
