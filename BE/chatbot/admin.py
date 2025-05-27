from django.contrib import admin
from .models import MedicalCondition, Symptom, ConditionSymptom, SpecialistRecommendation

@admin.register(MedicalCondition)
class MedicalConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity_level', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('severity_level', 'created_at')

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_common', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_common', 'created_at')

@admin.register(ConditionSymptom)
class ConditionSymptomAdmin(admin.ModelAdmin):
    list_display = ('condition', 'symptom', 'probability', 'is_primary')
    list_filter = ('is_primary', 'condition')
    search_fields = ('condition__name', 'symptom__name')

@admin.register(SpecialistRecommendation)
class SpecialistRecommendationAdmin(admin.ModelAdmin):
    list_display = ('condition', 'specialist_type', 'urgency_level')
    list_filter = ('urgency_level', 'specialist_type')
    search_fields = ('condition__name', 'specialist_type')