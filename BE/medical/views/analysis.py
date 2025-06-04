from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models.condition import MedicalCondition
from ..models.sympton import Symptom, ConditionSymptom
from ..models.recommendation import SpecialistRecommendation
from ..serializers.analysis import SymptomAnalysisSerializer, MedicalConditionSerializer
from django.db.models import Q



class SymptomAnalysisView(APIView):
    """
    Analyze user symptoms and return possible conditions with recommendations
    """
    def post(self, request):
        serializer = SymptomAnalysisSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Simple keyword-based analysis
            results = self.analyze_symptoms(data)

            return Response(results, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def analyze_symptoms(self, data):
        """
        Analyze symptoms and return recommendations
        """
        primary_symptoms = data.get('primary_symptoms', [])
        severity = data.get('severity', 5)
        duration = data.get('duration', '')
        additional_symptoms = data.get('additional_symptoms', [])

        # Get all symptoms from database
        all_symptoms = ' '.join(primary_symptoms + additional_symptoms).lower()

        # Find matching conditions
        conditions_scores = {}
        conditions = MedicalCondition.objects.all()

        for condition in conditions:
            score = 0
            condition_symptoms = ConditionSymptom.objects.filter(condition=condition)

            for cs in condition_symptoms:
                if cs.symptom.name.lower() in all_symptoms:
                    score += cs.probability
                    if cs.is_primary:
                        score += 0.2  # Bonus for primary symptoms

            # Severity adjustment
            if severity >= 7:
                score += 0.1

            if score > 0:
                conditions_scores[condition] = score

        # Sort by score
        sorted_conditions = sorted(conditions_scores.items(), key=lambda x: x[1], reverse=True)

        if not sorted_conditions:
            return {
                'most_likely': None,
                'confidence': 0,
                'recommendations': [{
                    'specialist': 'General Practitioner',
                    'urgency': 'MEDIUM',
                    'notes': 'Please consult a doctor for proper diagnosis'
                }]
            }

        # Get top condition
        top_condition, confidence = sorted_conditions[0]

        # Get recommendations for top condition
        recommendations = SpecialistRecommendation.objects.filter(condition=top_condition)

        return {
            'most_likely': {
                'name': top_condition.name,
                'description': top_condition.description,
                'severity': top_condition.severity_level
            },
            'confidence': min(confidence, 1.0),
            'recommendations': [
                {
                    'specialist': rec.specialist_type,
                    'urgency': rec.urgency_level,
                    'notes': rec.notes
                } for rec in recommendations
            ],
            'all_matches': [
                {
                    'name': condition.name,
                    'confidence': min(score, 1.0)
                } for condition, score in sorted_conditions[:3]
            ]
        }

class MedicalKnowledgeView(APIView):
    """
    Get medical knowledge base data
    """
    def get(self, request):
        conditions = MedicalCondition.objects.all()
        symptoms = Symptom.objects.all()

        return Response({
            'conditions': MedicalConditionSerializer(conditions, many=True).data,
            'common_symptoms': [s.name for s in symptoms.filter(is_common=True)]
        })