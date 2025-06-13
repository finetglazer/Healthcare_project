# BE/medical/views/chatbot.py
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

# Import timezone if not already imported
from django.utils import timezone


logger = logging.getLogger(__name__)

class ChatbotAnalysisView(APIView):
    """
    Enhanced chatbot analysis endpoint with progressive symptom collection
    """
    permission_classes = [AllowAny]  # Add this line

    def __init__(self):
        super().__init__()
        self.chatbot_engine = ChatbotEngine()
        self.analyzer = EnhancedSymptomAnalyzer()

    def post(self, request):
        """
        Analyze symptoms with progressive chatbot logic

        Expected input:
        {
            "conversation_step": "primary_symptoms",
            "user_inputs": {
                "primary_symptoms": ["Fever and body aches"],
                "severity": 7,
                "duration": "3 days"
            },
            "session_id": "unique_session_id"
        }
        """
        try:
            # Validate input
            serializer = ChatbotAnalysisSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid input data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data

            # Get or create conversation session
            session_id = data.get('session_id')
            conversation_step = data.get('conversation_step')
            user_inputs = data.get('user_inputs', {})

            # Process with chatbot engine
            result = self.chatbot_engine.process_conversation_step(
                step=conversation_step,
                inputs=user_inputs,
                session_id=session_id
            )

            # If analysis is complete, run full symptom analysis
            if result.get('analysis_complete'):
                analysis_result = self.run_full_analysis(user_inputs)
                result['analysis'] = analysis_result

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Chatbot analysis error: {e}")
            return Response({
                'error': 'Analysis failed',
                'message': 'Unable to process your symptoms. Please try again.',
                'fallback_recommendation': {
                    'message': 'Please consult a healthcare provider for proper diagnosis.',
                    'specialist': 'General Practitioner',
                    'urgency': 'MEDIUM'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def run_full_analysis(self, user_inputs):
        """Run comprehensive symptom analysis"""
        try:
            # Use enhanced analyzer with probability matrix
            result = self.analyzer.analyze_symptoms_advanced(user_inputs)

            # Add urgency detection
            urgency_level = self.detect_urgency(user_inputs, result)
            result['urgency'] = urgency_level

            # Add medical disclaimers
            result['disclaimers'] = self.get_medical_disclaimers(urgency_level)

            return result

        except Exception as e:
            logger.error(f"Full analysis error: {e}")
            return self.get_fallback_analysis()

    def detect_urgency(self, inputs, analysis_result):
        """Detect urgency level based on symptoms"""
        high_urgency_symptoms = [
            'difficulty breathing', 'chest pain', 'severe headache',
            'high fever', 'loss of consciousness', 'severe pain'
        ]

        severity = inputs.get('severity', 0)
        all_symptoms = ' '.join(
            inputs.get('primary_symptoms', []) +
            inputs.get('additional_symptoms', [])
        ).lower()

        # Check for urgent symptoms
        if any(urgent in all_symptoms for urgent in high_urgency_symptoms):
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

    def get_fallback_analysis(self):
        """Fallback analysis when main engine fails"""
        return {
            'most_likely': {
                'name': 'Unable to determine',
                'description': 'Analysis could not be completed',
                'confidence': 0.0
            },
            'recommendations': [{
                'specialist': 'General Practitioner',
                'urgency': 'MEDIUM',
                'notes': 'Please consult a healthcare provider for proper diagnosis'
            }],
            'disclaimers': self.get_medical_disclaimers('MEDIUM')
        }


class KnowledgeBaseView(APIView):
    """
    Serve knowledge base data for chatbot
    """

    permission_classes = [AllowAny]  # Add this line

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request):
        """
        Get knowledge base data with caching
        """
        try:
            # Check cache first
            cached_data = cache.get('knowledge_base_data')
            if cached_data:
                return Response(cached_data)

            analyzer = EnhancedSymptomAnalyzer()

            # Get comprehensive knowledge base data
            kb_data = {
                'conditions': self.get_conditions_data(analyzer),
                'symptoms': self.get_symptoms_data(analyzer),
                'conversation_flows': self.get_conversation_flows(),
                'probability_matrix': self.get_probability_matrix(analyzer),
                'metadata': {
                    'version': '2.0',
                    'last_updated': analyzer.knowledge_base.get('metadata', {}).get('created', 'Unknown'),
                    'total_conditions': len(analyzer.knowledge_base.get('conditions', {}))
                }
            }

            # Cache the data
            cache.set('knowledge_base_data', kb_data, 60 * 15)

            return Response(kb_data)

        except Exception as e:
            logger.error(f"Knowledge base error: {e}")
            return Response({
                'error': 'Knowledge base unavailable',
                'message': 'Unable to load medical knowledge base'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def get_conditions_data(self, analyzer):
        """Get conditions data from knowledge base"""
        conditions = analyzer.knowledge_base.get('conditions', {})
        return {
            condition_key: {
                'name': condition_data.get('name'),
                'description': condition_data.get('description'),
                'severity_level': condition_data.get('severity_level'),
                'primary_symptoms': condition_data.get('symptoms', [])[:5],  # Top 5 symptoms
                'sources': condition_data.get('sources', [])
            }
            for condition_key, condition_data in conditions.items()
        }

    def get_symptoms_data(self, analyzer):
        """Get symptoms data from knowledge base"""
        symptoms_index = analyzer.knowledge_base.get('symptoms_index', {})
        common_symptoms = []

        for symptom, data in symptoms_index.items():
            if data.get('frequency', 0) > 0.5:  # Common symptoms
                common_symptoms.append({
                    'name': symptom,
                    'frequency': data.get('frequency', 0),
                    'conditions': data.get('conditions', [])
                })

        return sorted(common_symptoms, key=lambda x: x['frequency'], reverse=True)

    def get_conversation_flows(self):
        """Get predefined conversation flows"""
        return {
            'primary_flow': [
                'greeting',
                'primary_symptoms',
                'severity',
                'duration',
                'additional_symptoms',
                'analysis'
            ],
            'skip_conditions': {
                'no_fever': ['temperature_check'],
                'mild_symptoms': ['emergency_check']
            }
        }

    def get_probability_matrix(self, analyzer):
        """Get simplified probability matrix for frontend use"""
        full_matrix = analyzer.probability_matrix or {}

        # Return simplified version for frontend
        simplified_matrix = {}
        for condition, symptoms in full_matrix.items():
            simplified_matrix[condition] = {
                symptom: prob for symptom, prob in symptoms.items()
                if prob > 0.3  # Only include significant probabilities
            }

        return simplified_matrix


class SymptomValidationView(APIView):
    """
    Validate and normalize symptom inputs
    """

    permission_classes = [AllowAny]  # Add this line

    def post(self, request):
        """
        Validate symptom inputs against knowledge base
        """
        try:
            serializer = SymptomValidationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            symptoms = serializer.validated_data.get('symptoms', [])

            # Validate and normalize symptoms
            analyzer = EnhancedSymptomAnalyzer()
            validation_results = []

            for symptom in symptoms:
                result = self.validate_single_symptom(symptom, analyzer)
                validation_results.append(result)

            return Response({
                'validation_results': validation_results,
                'valid_symptoms': [r for r in validation_results if r['is_valid']],
                'suggestions': self.get_symptom_suggestions(symptoms, analyzer)
            })

        except Exception as e:
            logger.error(f"Symptom validation error: {e}")
            return Response({
                'error': 'Validation failed',
                'message': 'Unable to validate symptoms'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def validate_single_symptom(self, symptom, analyzer):
        """Validate a single symptom"""
        symptom_lower = symptom.lower().strip()

        # Check if symptom exists in knowledge base
        symptoms_index = analyzer.knowledge_base.get('symptoms_index', {})

        # Direct match
        if symptom_lower in symptoms_index:
            return {
                'original': symptom,
                'normalized': symptom_lower,
                'is_valid': True,
                'confidence': 1.0,
                'conditions': symptoms_index[symptom_lower].get('conditions', [])
            }

        # Fuzzy match
        best_match = self.find_best_symptom_match(symptom_lower, symptoms_index)
        if best_match:
            return {
                'original': symptom,
                'normalized': best_match['symptom'],
                'is_valid': True,
                'confidence': best_match['confidence'],
                'conditions': symptoms_index[best_match['symptom']].get('conditions', [])
            }

        # No match found
        return {
            'original': symptom,
            'normalized': symptom_lower,
            'is_valid': False,
            'confidence': 0.0,
            'conditions': []
        }

    def find_best_symptom_match(self, symptom, symptoms_index):
        """Find best matching symptom using fuzzy matching"""
        from difflib import SequenceMatcher

        best_match = None
        best_confidence = 0.0

        for known_symptom in symptoms_index.keys():
            # Check if symptom is contained in known symptom or vice versa
            if symptom in known_symptom or known_symptom in symptom:
                confidence = 0.8
            else:
                # Use sequence matching
                confidence = SequenceMatcher(None, symptom, known_symptom).ratio()

            if confidence > best_confidence and confidence > 0.6:
                best_confidence = confidence
                best_match = {
                    'symptom': known_symptom,
                    'confidence': confidence
                }

        return best_match

    def get_symptom_suggestions(self, symptoms, analyzer):
        """Get symptom suggestions based on partial matches"""
        suggestions = []
        symptoms_index = analyzer.knowledge_base.get('symptoms_index', {})

        for symptom in symptoms:
            symptom_lower = symptom.lower()

            # Find partial matches
            partial_matches = [
                known_symptom for known_symptom in symptoms_index.keys()
                if symptom_lower in known_symptom or known_symptom in symptom_lower
            ]

            if partial_matches:
                suggestions.extend(partial_matches[:3])  # Top 3 suggestions

        return list(set(suggestions))  # Remove duplicates


# BE/medical/views/chatbot.py - Additional Views (Append to existing file)

class ChatbotFeedbackView(APIView):
    """
    Collect user feedback on chatbot interactions
    """

    def post(self, request):
        """
        Submit feedback for chatbot session

        Expected input:
        {
            "session_id": "unique_session_id",
            "satisfaction_rating": 4,
            "feedback_text": "Very helpful, but could be faster",
            "was_helpful": true,
            "suggested_improvements": ["Faster response", "More questions"]
        }
        """
        try:
            # Validate input
            session_id = request.data.get('session_id')
            satisfaction_rating = request.data.get('satisfaction_rating')
            feedback_text = request.data.get('feedback_text', '')
            was_helpful = request.data.get('was_helpful', True)
            suggested_improvements = request.data.get('suggested_improvements', [])

            if not session_id:
                return Response({
                    'error': 'session_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            if satisfaction_rating is not None and not (1 <= satisfaction_rating <= 5):
                return Response({
                    'error': 'satisfaction_rating must be between 1 and 5'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Store feedback (in a real app, you'd save to database)
            feedback_data = {
                'session_id': session_id,
                'satisfaction_rating': satisfaction_rating,
                'feedback_text': feedback_text,
                'was_helpful': was_helpful,
                'suggested_improvements': suggested_improvements,
                'timestamp': str(timezone.now()),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self.get_client_ip(request)
            }

            # Cache feedback for analytics
            feedback_key = f'chatbot_feedback_{session_id}'
            cache.set(feedback_key, feedback_data, 60 * 60 * 24)  # 24 hours

            # Log feedback for monitoring
            logger.info(f"Chatbot feedback received: Session {session_id}, Rating: {satisfaction_rating}")

            return Response({
                'message': 'Thank you for your feedback!',
                'feedback_id': session_id,
                'status': 'received'
            })

        except Exception as e:
            logger.error(f"Feedback submission error: {e}")
            return Response({
                'error': 'Unable to submit feedback',
                'message': 'Please try again later'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ConversationSessionView(APIView):
    """
    Manage conversation sessions
    """

    def get(self, request, session_id):
        """Get conversation session data"""
        try:
            session_key = f'chatbot_session_{session_id}'
            session_data = cache.get(session_key)

            if not session_data:
                return Response({
                    'error': 'Session not found',
                    'message': 'Session may have expired or does not exist'
                }, status=status.HTTP_404_NOT_FOUND)

            # Return session summary (without sensitive data)
            return Response({
                'session_id': session_id,
                'current_step': session_data.get('current_step'),
                'steps_completed': len(session_data.get('conversation_history', [])),
                'analysis_complete': session_data.get('analysis_results') is not None,
                'created_at': session_data.get('created_at'),
                'progress_percentage': self.calculate_progress(session_data)
            })

        except Exception as e:
            logger.error(f"Session retrieval error: {e}")
            return Response({
                'error': 'Unable to retrieve session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, session_id):
        """Clear conversation session"""
        try:
            session_key = f'chatbot_session_{session_id}'
            cache.delete(session_key)

            return Response({
                'message': 'Session cleared successfully'
            })

        except Exception as e:
            logger.error(f"Session deletion error: {e}")
            return Response({
                'error': 'Unable to clear session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def calculate_progress(self, session_data):
        """Calculate conversation progress percentage"""
        total_steps = ['greeting', 'primary_symptoms', 'severity', 'duration',
                       'additional_symptoms', 'differential_questions', 'analysis']

        current_step = session_data.get('current_step', 'greeting')

        if current_step in total_steps:
            current_index = total_steps.index(current_step)
            return int((current_index + 1) / len(total_steps) * 100)

        return 0

