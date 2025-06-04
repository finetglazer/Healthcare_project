from rest_framework import serializers
from ..models.condition import MedicalCondition
from ..models.sympton import Symptom, ConditionSymptom
from ..models.recommendation import SpecialistRecommendation

class MedicalConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCondition
        fields = '__all__'

class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = '__all__'

class SymptomAnalysisSerializer(serializers.Serializer):
    primary_symptoms = serializers.ListField(child=serializers.CharField())
    severity = serializers.IntegerField(min_value=1, max_value=10)
    duration = serializers.CharField()
    additional_symptoms = serializers.ListField(child=serializers.CharField(), required=False)