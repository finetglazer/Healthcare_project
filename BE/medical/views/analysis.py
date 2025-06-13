# BE/medical/views/analysis.py - Updated version
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models.condition import MedicalCondition
from ..models.symptom import Symptom, ConditionSymptom
from ..models.recommendation import SpecialistRecommendation
from ..serializers.analysis import SymptomAnalysisSerializer, MedicalConditionSerializer
from ..services.enhanced_analyzer import EnhancedSymptomAnalyzer
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class SymptomAnalysisView(APIView):
    """
    Enhanced symptom analysis using comprehensive knowledge base
    """

    def __init__(self):
        super().__init__()
        self.analyzer = EnhancedSymptomAnalyzer()

    def post(self, request):
        """
        Analyze symptoms with enhanced engine

        Expected input:
        {
            "primary_symptoms": ["Fever and body aches", "Fatigue"],
            "severity": 7,
            "duration": "3 days",
            "additional_symptoms": ["Headache", "Chills"],
            "age": 35,
            "medical_history": ["Asthma"]
        }
        """
        try:
            # Validate input
            serializer = SymptomAnalysisSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data

            # Use enhanced analyzer
            try:
                results = self.analyzer.analyze_symptoms_advanced(data)

                # Add chatbot-friendly response format
                chatbot_response = self.format_for_chatbot(results)
                results['chatbot_response'] = chatbot_response

                return Response(results, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Enhanced analysis failed: {e}")
                # Fallback to simple analysis
                fallback_results = self.simple_analysis(data)
                fallback_results['note'] = 'Using simplified analysis due to technical issues'
                return Response(fallback_results, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Analysis request failed: {e}")
            return Response(
                {'error': 'Analysis temporarily unavailable'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def format_for_chatbot(self, results: dict) -> dict:
        """Format results for chatbot consumption"""
        most_likely = results.get('most_likely', {})
        recommendations = results.get('recommendations', {})

        # Create user-friendly message
        condition = most_likely.get('condition', 'Unknown')
        confidence = most_likely.get('confidence', 0)

        if confidence >= 0.7:
            confidence_text = "high confidence"
        elif confidence >= 0.4:
            confidence_text = "moderate confidence"
        else:
            confidence_text = "low confidence"

        # Build chatbot message
        message = f"Based on your symptoms, with **{confidence_text}**, you may have **{condition}**."

        # Add recommendations
        specialist = recommendations.get('specialist', 'healthcare provider')
        urgency = recommendations.get('urgency', 'MEDIUM')

        if urgency == 'HIGH':
            message += f"\n\n🚨 **Important**: Please see a {specialist} **immediately**."
        elif urgency == 'MEDIUM':
            message += f"\n\n📅 **Recommendation**: Schedule an appointment with a {specialist} soon."
        else:
            message += f"\n\n💡 **Suggestion**: Consider consulting a {specialist} if symptoms persist."

        # Add next steps
        next_steps = results.get('next_steps', [])
        if next_steps:
            message += "\n\n**Next Steps:**\n"
            for i, step in enumerate(next_steps[:3], 1):  # Limit to 3 steps
                message += f"{i}. {step}\n"

        return {
            'message': message,
            'condition': condition,
            'confidence': confidence,
            'confidence_text': confidence_text,
            'urgency': urgency,
            'specialist': specialist,
            'action_needed': urgency in ['HIGH', 'URGENT']
        }

    def simple_analysis(self, data):
        """Fallback simple analysis using existing logic"""
        primary_symptoms = data.get('primary_symptoms', [])
        severity = data.get('severity', 5)
        duration = data.get('duration', '')
        additional_symptoms = data.get('additional_symptoms', [])

        # Simple keyword-based analysis (existing logic)
        all_symptoms = ' '.join(primary_symptoms + additional_symptoms).lower()

        conditions_scores = {}
        conditions = MedicalCondition.objects.all()

        for condition in conditions:
            score = 0
            condition_symptoms = ConditionSymptom.objects.filter(condition=condition)

            for cs in condition_symptoms:
                if cs.symptom.name.lower() in all_symptoms:
                    score += cs.probability
                    if cs.is_primary:
                        score += 0.2

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
                'severity': top_condition.severity_level,
                'confidence': min(confidence, 1.0)
            },
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
    Get medical knowledge base data and statistics
    """
    def get(self, request):
        conditions = MedicalCondition.objects.all()
        symptoms = Symptom.objects.all()

        # Get knowledge base statistics
        try:
            analyzer = EnhancedSymptomAnalyzer()
            kb_stats = {
                'knowledge_base_loaded': analyzer.knowledge_base is not None,
                'total_conditions': len(analyzer.probability_matrix) if analyzer.probability_matrix else 0,
                'has_differential_rules': bool(analyzer.diff_diagnosis)
            }
        except:
            kb_stats = {
                'knowledge_base_loaded': False,
                'total_conditions': 0,
                'has_differential_rules': False
            }

        return Response({
            'conditions': MedicalConditionSerializer(conditions, many=True).data,
            'common_symptoms': [s.name for s in symptoms.filter(is_common=True)],
            'knowledge_base_stats': kb_stats
        })


class ChatbotIntegrationView(APIView):
    """
    Specialized endpoint for chatbot integration
    """

    def post(self, request):
        """
        Simplified endpoint specifically for chatbot

        Input format from chatbot flow:
        {
            "conversation_data": {
                "primary_symptoms": "Fever and body aches",
                "severity": 7,
                "duration": "3 days",
                "additional_symptoms": ["Headache", "Fatigue"]
            }
        }
        """
        try:
            conversation_data = request.data.get('conversation_data', {})

            # Transform chatbot data to analyzer format
            analyzer_input = {
                'primary_symptoms': [conversation_data.get('primary_symptoms', '')],
                'severity': conversation_data.get('severity', 5),
                'duration': conversation_data.get('duration', ''),
                'additional_symptoms': conversation_data.get('additional_symptoms', [])
            }

            # Remove empty values
            analyzer_input['primary_symptoms'] = [s for s in analyzer_input['primary_symptoms'] if s]

            # Analyze
            analyzer = EnhancedSymptomAnalyzer()
            results = analyzer.analyze_symptoms_advanced(analyzer_input)

            # Return chatbot-optimized response
            return Response({
                'success': True,
                'analysis': results.get('chatbot_response', {}),
                'detailed_results': results,
                'recommended_doctors': self.get_recommended_doctors(results)
            })

        except Exception as e:
            logger.error(f"Chatbot integration error: {e}")
            return Response({
                'success': False,
                'error': 'Analysis temporarily unavailable',
                'fallback_message': 'Please consult with a healthcare provider for proper evaluation of your symptoms.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_recommended_doctors(self, analysis_results):
        """Get recommended doctors based on analysis"""
        recommendations = analysis_results.get('recommendations', {})
        specialist_type = recommendations.get('specialist', 'General Practitioner')

        # This would integrate with your doctor models
        # For now, return a simple structure
        return {
            'specialist_type': specialist_type,
            'urgency': recommendations.get('urgency', 'MEDIUM'),
            'search_url': f'/find-doctors?specialty={specialist_type.replace(" ", "%20")}'
        }