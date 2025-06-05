from django.contrib import admin
from .models import Laboratory, LabTest, LabOrder, LabResult

@admin.register(Laboratory)
class LaboratoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'lab_type', 'location', 'is_active']
    list_filter = ['lab_type', 'is_active']
    search_fields = ['name', 'location']

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'cost', 'laboratory', 'is_active']
    list_filter = ['category', 'laboratory', 'is_active']
    search_fields = ['name', 'code']

@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'patient', 'doctor', 'laboratory', 'status', 'created_at']
    list_filter = ['status', 'priority', 'laboratory']
    search_fields = ['order_number', 'patient__user__first_name', 'patient__user__last_name']

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ['test', 'value', 'unit', 'status', 'result_date']
    list_filter = ['status', 'result_date']
    search_fields = ['test__name', 'order__order_number']