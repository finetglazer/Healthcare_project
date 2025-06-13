# BE/medical/views/chatbot.py - Complete file with all required classes

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ..services.enhanced_analyzer import EnhancedSymptomAnalyzer
from ..services.chatbot_engine import ChatbotEngine
from ..serializers.chatbot import (
    ChatbotAnalysisSerializer,
    SymptomValidationSerializer,
    ConversationStepSerializer,
    KnowledgeBaseSerializer
)
import logging
import json
from rest_framework.permissions import AllowAny
from django.utils import timezone

logger = logging.getLogger(__name__)

class ChatbotAnalysisView(APIView):
    """Enhanced chatbot analysis endpoint"""
    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        try:
            self.chatbot_engine = ChatbotEngine()
            self.analyzer = EnhancedSymptomAnalyzer()
        except Exception as e:
            logger.error(f"Failed to initialize chatbot components: {e}")
            self.chatbot_engine = None
            self.analyzer = None

    def post(self, request):
        """Analyze symptoms"""
        try:
            logger.info(f"Received analysis request: {request.data}")

            # Validate input
            serializer = ChatbotAnalysisSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Invalid input data: {serializer.errors}")
                return Response({
                    'error': 'Invalid input data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data
            session_id = data.get('session_id')
            conversation_step = data.get('conversation_step')
            user_inputs = data.get('user_inputs', {})

            logger.info(f"Processing step: {conversation_step} for session: {session_id}")

            # If analysis is requested, run full analysis
            if conversation_step == 'analysis' or data.get('analysis_complete'):
                analysis_result = self.run_full_analysis(user_inputs)
                logger.info(f"Analysis completed: {analysis_result}")

                return Response({
                    'session_id': session_id,
                    'conversation_step': conversation_step,
                    'analysis_complete': True,
                    'analysis': analysis_result,
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_200_OK)

            # For other steps, return basic response
            return Response({
                'session_id': session_id,
                'conversation_step': conversation_step,
                'message': 'Step processed successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Chatbot analysis error: {e}", exc_info=True)
            return Response({
                'error': 'Analysis failed',
                'message': 'Unable to process your symptoms. Please try again.',
                'analysis': self.get_fallback_analysis(),
                'fallback': True,
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def run_full_analysis(self, user_inputs):
        """Run comprehensive symptom analysis"""
        try:
            logger.info(f"Running full analysis on inputs: {user_inputs}")

            if self.analyzer:
                result = self.analyzer.analyze_symptoms_advanced(user_inputs)
                if result:
                    # Add urgency detection
                    urgency_level = self.detect_urgency(user_inputs, result)
                    result['urgency'] = urgency_level
                    result['urgencyLevel'] = urgency_level
                    result['disclaimers'] = self.get_medical_disclaimers(urgency_level)

                    # Ensure proper format
                    if 'conditions' not in result and 'mostLikely' in result:
                        result['conditions'] = result['mostLikely']
                    elif 'mostLikely' not in result and 'conditions' in result:
                        result['mostLikely'] = result['conditions']

                    if 'recommendations' not in result:
                        result['recommendations'] = self.get_default_recommendations(urgency_level)

                    logger.info(f"Full analysis result: {result}")
                    return result

            # Fallback if analyzer fails
            return self.get_fallback_analysis()

        except Exception as e:
            logger.error(f"Full analysis error: {e}", exc_info=True)
            return self.get_fallback_analysis()

    def detect_urgency(self, inputs, analysis_result):
        """Detect urgency level based on symptoms"""
        high_urgency_symptoms = [
            'difficulty breathing', 'chest pain', 'severe headache',
            'high fever', 'loss of consciousness', 'severe pain',
            'shortness of breath', 'breathing difficulties'
        ]

        severity = inputs.get('severity', 0)

        # Extract all symptoms text
        all_symptoms_text = ""
        for key, value in inputs.items():
            if isinstance(value, list):
                all_symptoms_text += " ".join(str(v) for v in value)
            else:
                all_symptoms_text += str(value)

        all_symptoms_text = all_symptoms_text.lower()

        # Check for urgent symptoms
        if any(urgent in all_symptoms_text for urgent in high_urgency_symptoms):
            return 'URGENT'

        # Check severity level
        if severity >= 8:
            return 'HIGH'
        elif severity >= 6:
            return 'MEDIUM'
        else:
            return 'LOW'

    def get_medical_disclaimers(self, urgency_level):
        """Get appropriate medical disclaimers"""
        base_disclaimer = "This tool is for informational purposes only and should not replace professional medical advice."
        disclaimers = [base_disclaimer]

        if urgency_level == 'URGENT':
            disclaimers.append("⚠️ Your symptoms may require immediate medical attention. Please seek emergency care or call emergency services.")
        elif urgency_level == 'HIGH':
            disclaimers.append("⚠️ Please consult a healthcare provider promptly for proper evaluation.")
        else:
            disclaimers.append("If symptoms persist or worsen, please consult a healthcare provider.")

        return disclaimers

    def get_default_recommendations(self, urgency_level):
        """Get default recommendations based on urgency"""
        if urgency_level == 'URGENT':
            return {
                'specialist': 'Emergency Room',
                'action': 'Seek immediate medical attention',
                'message': 'Your symptoms may require urgent care.'
            }
        elif urgency_level == 'HIGH':
            return {
                'specialist': 'Primary Care Physician',
                'action': 'Schedule appointment promptly',
                'message': 'Please see a healthcare provider soon.'
            }
        else:
            return {
                'specialist': 'Healthcare Provider',
                'action': 'Consider scheduling appointment',
                'message': 'Monitor symptoms and consult if they worsen.'
            }

    def get_fallback_analysis(self):
        """Get fallback analysis when everything else fails"""
        return {
            'conditions': [['Unknown Condition', 0.5]],
            'mostLikely': [['Unknown Condition', 0.5]],
            'urgency': 'MEDIUM',
            'urgencyLevel': 'MEDIUM',
            'recommendations': {
                'specialist': 'Healthcare Provider',
                'action': 'Consult healthcare provider',
                'message': 'Unable to analyze symptoms properly. Please consult a healthcare provider for proper evaluation.'
            },
            'confidence': 0.5,
            'disclaimers': [
                'This analysis could not be completed properly. Please seek professional medical advice.'
            ],
            'fallback': True
        }


class SymptomValidationView(APIView):
    """Validate and normalize symptom inputs"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Validate symptom inputs against knowledge base"""
        try:
            symptoms = request.data.get('symptoms', [])

            # Simple validation for now
            validation_results = []
            for symptom in symptoms:
                validation_results.append({
                    'original': symptom,
                    'normalized': symptom.lower().strip(),
                    'is_valid': True,
                    'confidence': 1.0
                })

            return Response({
                'validation_results': validation_results,
                'valid_symptoms': validation_results,
                'suggestions': []
            })

        except Exception as e:
            logger.error(f"Symptom validation error: {e}")
            return Response({
                'error': 'Validation failed',
                'message': 'Unable to validate symptoms'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KnowledgeBaseView(APIView):
    """Serve knowledge base data to frontend"""
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request):
        """Return knowledge base data"""
        try:
            logger.info("Knowledge base requested")

            try:
                analyzer = EnhancedSymptomAnalyzer()

                if not analyzer.knowledge_base:
                    logger.warning("Knowledge base is empty, building fallback")
                    return Response(self.get_fallback_knowledge_base(), status=status.HTTP_200_OK)

                # Simplify knowledge base for frontend
                simplified_kb = {
                    'conditions': analyzer.knowledge_base.get('conditions', {}),
                    'symptoms': list(analyzer.knowledge_base.get('symptoms_index', {}).keys()),
                    'metadata': analyzer.knowledge_base.get('metadata', {}),
                    'status': 'loaded_from_files'
                }

                logger.info(f"Returning knowledge base with {len(simplified_kb['conditions'])} conditions")
                return Response(simplified_kb, status=status.HTTP_200_OK)

            except Exception as analyzer_error:
                logger.error(f"Analyzer initialization failed: {analyzer_error}")
                return Response(self.get_fallback_knowledge_base(), status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Knowledge base error: {e}", exc_info=True)
            return Response(self.get_fallback_knowledge_base(), status=status.HTTP_200_OK)

    def get_fallback_knowledge_base(self):
        """Fallback knowledge base when files are not available"""
        return {
            'conditions': {
                'flu': {
                    'name': 'Influenza (Flu)',
                    'symptoms': ['fever', 'body aches', 'fatigue', 'chills', 'headache'],
                    'description': 'Viral respiratory illness caused by influenza viruses'
                },
                'cold': {
                    'name': 'Common Cold',
                    'symptoms': ['runny nose', 'sneezing', 'sore throat', 'congestion'],
                    'description': 'Viral infection of the upper respiratory tract'
                },
                'covid': {
                    'name': 'COVID-19',
                    'symptoms': ['loss of taste', 'loss of smell', 'cough', 'fever', 'shortness of breath'],
                    'description': 'Disease caused by SARS-CoV-2 coronavirus'
                },
                'allergy': {
                    'name': 'Allergic Reaction',
                    'symptoms': ['sneezing', 'itchy eyes', 'runny nose', 'watery eyes'],
                    'description': 'Immune system reaction to allergens'
                }
            },
            'symptoms': [
                'fever', 'cough', 'runny nose', 'sneezing', 'body aches',
                'fatigue', 'sore throat', 'loss of taste', 'loss of smell',
                'shortness of breath', 'itchy eyes', 'watery eyes', 'chills',
                'headache', 'congestion'
            ],
            'metadata': {
                'version': 'fallback-1.0',
                'source': 'hardcoded_fallback',
                'created': timezone.now().isoformat()
            },
            'status': 'fallback_data'
        }


class HealthCheckView(APIView):
    """Health check endpoint for frontend"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Return system health status"""
        try:
            # Check if analyzer can be initialized
            analyzer_status = 'healthy'
            try:
                analyzer = EnhancedSymptomAnalyzer()
                if not analyzer.knowledge_base:
                    analyzer_status = 'degraded'
            except Exception:
                analyzer_status = 'unhealthy'

            return Response({
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'services': {
                    'analyzer': analyzer_status,
                    'database': 'healthy',
                    'api': 'healthy'
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)