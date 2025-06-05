from django.contrib import admin
from .models import HealthRecord, VitalSigns, MedicalHistory, Allergy

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['record_id', 'patient', 'doctor', 'record_type', 'service_date', 'privacy_level']
    list_filter = ['record_type', 'privacy_level', 'service_date', 'is_verified']
    search_fields = ['record_id', 'patient__user__first_name', 'title']

@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
    list_display = ['patient', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'temperature', 'measured_at']
    list_filter = ['measured_at']
    search_fields = ['patient__user__first_name', 'patient__user__last_name']

@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'condition_name', 'status', 'diagnosed_date', 'severity']
    list_filter = ['status', 'severity', 'diagnosed_date']
    search_fields = ['patient__user__first_name', 'condition_name', 'icd_code']

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ['patient', 'allergen_name', 'allergen_type', 'severity', 'is_active']
    list_filter = ['allergen_type', 'severity', 'is_active']
    search_fields = ['patient__user__first_name', 'allergen_name']
