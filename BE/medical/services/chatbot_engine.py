# BE/medical/services/chatbot_engine.py
import json
import logging
from typing import Dict, List, Any, Optional
from django.core.cache import cache
from .enhanced_analyzer import EnhancedSymptomAnalyzer

logger = logging.getLogger(__name__)

class ChatbotEngine:
    """
    Progressive symptom collection engine with smart questioning
    """

    def __init__(self):
        self.analyzer = EnhancedSymptomAnalyzer()
        self.conversation_steps = [
            'greeting',
            'primary_symptoms',
            'severity',
            'duration',
            'additional_symptoms',
            'differential_questions',
            'analysis'
        ]

        # Define condition-specific questions for differential diagnosis
        self.differential_questions = {
            'flu_vs_cold': {
                'question': "Do you have significant body aches and muscle pain?",
                'options': ['Yes, severe body aches', 'Mild aches', 'No body aches'],
                'scoring': {
                    'flu': {'Yes, severe body aches': 0.8, 'Mild aches': 0.3, 'No body aches': 0.1},
                    'cold': {'Yes, severe body aches': 0.1, 'Mild aches': 0.4, 'No body aches': 0.7}
                }
            },
            'covid_vs_flu': {
                'question': "Have you experienced loss of taste or smell?",
                'options': ['Complete loss', 'Partial loss', 'No change'],
                'scoring': {
                    'covid-19': {'Complete loss': 0.9, 'Partial loss': 0.6, 'No change': 0.2},
                    'flu': {'Complete loss': 0.1, 'Partial loss': 0.2, 'No change': 0.8}
                }
            },
            'allergy_vs_cold': {
                'question': "Are your symptoms seasonal or triggered by specific environments?",
                'options': ['Seasonal pattern', 'Environmental triggers', 'No pattern'],
                'scoring': {
                    'allergy': {'Seasonal pattern': 0.8, 'Environmental triggers': 0.9, 'No pattern': 0.2},
                    'cold': {'Seasonal pattern': 0.2, 'Environmental triggers': 0.1, 'No pattern': 0.7}
                }
            }
        }

    def process_conversation_step(self, step: str, inputs: Dict, session_id: str) -> Dict:
        """
        Process a conversation step with smart questioning logic
        """
        try:
            # Get or create session data
            session_data = self.get_session_data(session_id)

            # Update session with new inputs
            session_data['inputs'].update(inputs)
            session_data['current_step'] = step

            # Process the current step
            if step == 'greeting':
                result = self.handle_greeting()
            elif step == 'primary_symptoms':
                result = self.handle_primary_symptoms(inputs, session_data)
            elif step == 'severity':
                result = self.handle_severity(inputs, session_data)
            elif step == 'duration':
                result = self.handle_duration(inputs, session_data)
            elif step == 'additional_symptoms':
                result = self.handle_additional_symptoms(inputs, session_data)
            elif step == 'differential_questions':
                result = self.handle_differential_questions(inputs, session_data)
            elif step == 'analysis':
                result = self.handle_analysis(session_data)
            else:
                result = self.handle_unknown_step(step)

            # Update session data
            session_data['conversation_history'].append({
                'step': step,
                'inputs': inputs,
                'response': result
            })

            # Save session
            self.save_session_data(session_id, session_data)

            return result

        except Exception as e:
            logger.error(f"Conversation step error: {e}")
            return self.get_error_response(f"Error processing step: {step}")

    def handle_greeting(self) -> Dict:
        """Handle initial greeting"""
        return {
            'message': "Hello! I'm your medical assistant. I'll help you understand your symptoms through a few questions.",
            'next_step': 'primary_symptoms',
            'question': {
                'type': 'multiple_choice',
                'text': "What are your main symptoms?",
                'options': [
                    'Fever and body aches',
                    'Runny nose and sneezing',
                    'Cough and sore throat',
                    'Multiple symptoms',
                    'Other symptoms'
                ]
            },
            'progress': 10
        }

    def handle_primary_symptoms(self, inputs: Dict, session_data: Dict) -> Dict:
        """Handle primary symptoms with smart follow-up"""
        primary_symptoms = inputs.get('primary_symptoms', [])

        # Analyze primary symptoms to determine next question
        preliminary_analysis = self.get_preliminary_analysis(primary_symptoms)

        return {
            'message': f"I understand you're experiencing: {', '.join(primary_symptoms)}",
            'next_step': 'severity',
            'question': {
                'type': 'scale',
                'text': "How would you rate the severity of your symptoms?",
                'scale': {
                    'min': 1,
                    'max': 10,
                    'labels': {
                        '1-3': 'Mild',
                        '4-6': 'Moderate',
                        '7-8': 'Severe',
                        '9-10': 'Very Severe'
                    }
                }
            },
            'progress': 30,
            'preliminary_conditions': preliminary_analysis
        }

    def handle_severity(self, inputs: Dict, session_data: Dict) -> Dict:
        """Handle severity assessment"""
        severity = inputs.get('severity', 5)

        # Check for urgent symptoms
        if severity >= 8:
            urgency_message = "⚠️ High severity symptoms may require prompt medical attention."
        else:
            urgency_message = ""

        return {
            'message': f"Severity level: {severity}/10. {urgency_message}",
            'next_step': 'duration',
            'question': {
                'type': 'multiple_choice',
                'text': "How long have you been experiencing these symptoms?",
                'options': [
                    'Less than 24 hours',
                    '1-3 days',
                    '4-7 days',
                    'More than a week',
                    'Recurring episodes'
                ]
            },
            'progress': 50,
            'urgency_detected': severity >= 8
        }

    def handle_duration(self, inputs: Dict, session_data: Dict) -> Dict:
        """Handle symptom duration"""
        duration = inputs.get('duration', '')

        # Determine if we need additional symptoms based on current info
        need_additional = self.should_ask_additional_symptoms(session_data['inputs'])

        if need_additional:
            next_step = 'additional_symptoms'
            question = {
                'type': 'checkbox',
                'text': "Do you have any of these additional symptoms?",
                'options': self.get_relevant_additional_symptoms(session_data['inputs'])
            }
        else:
            next_step = 'differential_questions'
            question = self.get_differential_question(session_data['inputs'])

        return {
            'message': f"Duration: {duration}",
            'next_step': next_step,
            'question': question,
            'progress': 70
        }

    def handle_additional_symptoms(self, inputs: Dict, session_data: Dict) -> Dict:
        """Handle additional symptoms collection"""
        additional_symptoms = inputs.get('additional_symptoms', [])

        # Get differential question based on all symptoms
        all_inputs = session_data['inputs'].copy()
        all_inputs.update(inputs)

        differential_question = self.get_differential_question(all_inputs)

        if differential_question:
            next_step = 'differential_questions'
            question = differential_question
            progress = 85
        else:
            # Skip differential questions, go straight to analysis
            next_step = 'analysis'
            question = None
            progress = 100

        return {
            'message': f"Additional symptoms noted: {', '.join(additional_symptoms) if additional_symptoms else 'None'}",
            'next_step': next_step,
            'question': question,
            'progress': progress
        }

    def handle_differential_questions(self, inputs: Dict, session_data: Dict) -> Dict:
        """Handle differential diagnosis questions"""
        differential_answer = inputs.get('differential_answer', '')

        # Store differential answer
        session_data['inputs']['differential_answer'] = differential_answer

        return {
            'message': "Thank you for the additional information. Analyzing your symptoms...",
            'next_step': 'analysis',
            'question': None,
            'progress': 100,
            'analysis_complete': True
        }

    def handle_analysis(self, session_data: Dict) -> Dict:
        """Handle final analysis"""
        return {
            'message': "Analysis complete! Here are your results:",
            'next_step': None,
            'question': None,
            'progress': 100,
            'analysis_complete': True
        }

    def get_preliminary_analysis(self, symptoms: List[str]) -> List[Dict]:
        """Get preliminary condition matches"""
        try:
            # Use knowledge base to find matching conditions
            conditions = self.analyzer.knowledge_base.get('conditions', {})
            matches = []

            symptoms_text = ' '.join(symptoms).lower()

            for condition_key, condition_data in conditions.items():
                condition_symptoms = condition_data.get('symptoms', [])
                score = 0

                for symptom in condition_symptoms:
                    if symptom.lower() in symptoms_text:
                        score += 1

                if score > 0:
                    matches.append({
                        'condition': condition_data.get('name'),
                        'match_score': score / len(condition_symptoms),
                        'key': condition_key
                    })

            # Return top 3 matches
            return sorted(matches, key=lambda x: x['match_score'], reverse=True)[:3]

        except Exception as e:
            logger.error(f"Preliminary analysis error: {e}")
            return []

    def should_ask_additional_symptoms(self, inputs: Dict) -> bool:
        """Determine if additional symptoms are needed"""
        primary_symptoms = inputs.get('primary_symptoms', [])
        severity = inputs.get('severity', 5)

        # Ask for additional symptoms if:
        # 1. Primary symptoms are vague
        # 2. Severity is high
        # 3. Preliminary analysis shows multiple possible conditions

        if severity >= 7:
            return True

        if len(primary_symptoms) <= 1:
            return True

        preliminary = self.get_preliminary_analysis(primary_symptoms)
        if len(preliminary) > 2:  # Multiple possible conditions
            return True

        return False

    def get_relevant_additional_symptoms(self, inputs: Dict) -> List[str]:
        """Get relevant additional symptoms based on primary symptoms"""
        primary_symptoms = inputs.get('primary_symptoms', [])
        symptoms_text = ' '.join(primary_symptoms).lower()

        # Symptom categories based on primary symptoms
        if any(term in symptoms_text for term in ['fever', 'body aches', 'fatigue']):
            return [
                'Headache',
                'Chills',
                'Muscle pain',
                'Nausea',
                'Loss of appetite',
                'Difficulty sleeping'
            ]
        elif any(term in symptoms_text for term in ['runny nose', 'sneezing', 'congestion']):
            return [
                'Itchy eyes',
                'Watery eyes',
                'Postnasal drip',
                'Facial pressure',
                'Reduced sense of smell',
                'Throat irritation'
            ]
        elif any(term in symptoms_text for term in ['cough', 'sore throat']):
            return [
                'Shortness of breath',
                'Chest tightness',
                'Wheezing',
                'Hoarse voice',
                'Difficulty swallowing',
                'Phlegm production'
            ]
        else:
            return [
                'Headache',
                'Fatigue',
                'Nausea',
                'Skin rash',
                'Joint pain',
                'Dizziness'
            ]

    def get_differential_question(self, inputs: Dict) -> Optional[Dict]:
        """Get differential diagnosis question based on symptoms"""
        primary_symptoms = inputs.get('primary_symptoms', [])
        symptoms_text = ' '.join(primary_symptoms).lower()

        # Determine which differential question to ask
        if any(term in symptoms_text for term in ['fever', 'body aches']) and \
                any(term in symptoms_text for term in ['runny nose', 'congestion']):
            return {
                'type': 'multiple_choice',
                'text': self.differential_questions['flu_vs_cold']['question'],
                'options': self.differential_questions['flu_vs_cold']['options'],
                'differential_type': 'flu_vs_cold'
            }
        elif any(term in symptoms_text for term in ['fever', 'cough']):
            return {
                'type': 'multiple_choice',
                'text': self.differential_questions['covid_vs_flu']['question'],
                'options': self.differential_questions['covid_vs_flu']['options'],
                'differential_type': 'covid_vs_flu'
            }
        elif any(term in symptoms_text for term in ['sneezing', 'runny nose']):
            return {
                'type': 'multiple_choice',
                'text': self.differential_questions['allergy_vs_cold']['question'],
                'options': self.differential_questions['allergy_vs_cold']['options'],
                'differential_type': 'allergy_vs_cold'
            }

        return None

    def get_session_data(self, session_id: str) -> Dict:
        """Get or create session data"""
        session_key = f'chatbot_session_{session_id}'
        session_data = cache.get(session_key)

        if not session_data:
            session_data = {
                'inputs': {},
                'current_step': 'greeting',
                'conversation_history': [],
                'created_at': str(json.dumps(str(cache._expire_info))),
                'analysis_results': None
            }

        return session_data

    def save_session_data(self, session_id: str, session_data: Dict):
        """Save session data to cache"""
        session_key = f'chatbot_session_{session_id}'
        # Save for 1 hour
        cache.set(session_key, session_data, 60 * 60)

    def handle_unknown_step(self, step: str) -> Dict:
        """Handle unknown conversation steps"""
        return {
            'error': f'Unknown conversation step: {step}',
            'message': 'I apologize, but I encountered an issue. Let me restart our conversation.',
            'next_step': 'greeting',
            'question': None,
            'progress': 0
        }

    def get_error_response(self, error_message: str) -> Dict:
        """Get standardized error response"""
        return {
            'error': True,
            'message': 'I apologize, but I encountered a technical issue. Please try again.',
            'error_details': error_message,
            'fallback_recommendation': {
                'message': 'Please consult a healthcare provider for proper medical evaluation.',
                'specialist': 'General Practitioner',
                'urgency': 'MEDIUM'
            }
        }

    def get_session_data(self, session_id):
        return cache.get(f"chatbot_session_{session_id}", {})