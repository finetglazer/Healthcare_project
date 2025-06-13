# BE/medical/services/enhanced_analyzer.py - Updated version
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from django.conf import settings
from django.core.cache import cache
from ..models.condition import MedicalCondition
from ..models.sympton import Symptom, ConditionSymptom
from ..models.recommendation import SpecialistRecommendation

logger = logging.getLogger(__name__)

class EnhancedSymptomAnalyzer:
    """
    Enhanced symptom analyzer with proper knowledge base integration
    """

    def __init__(self):
        self.knowledge_base_dir = self.get_knowledge_base_path()
        self.knowledge_base = None
        self.probability_matrix = None
        self.diff_diagnosis = None
        self.symptoms_index = None

        # Load knowledge base
        self.load_knowledge_base()

    def get_knowledge_base_path(self):
        """Get knowledge base path with multiple fallback options"""
        possible_paths = [
            Path("medical_knowledge"),  # Relative to project root
            Path(settings.BASE_DIR) / "medical_knowledge",
            Path(settings.BASE_DIR) / "BE" / "medical_knowledge",
            ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"Using knowledge base at: {path}")
                return path

        # Create default path if none exists
        default_path = Path(settings.BASE_DIR) / "medical_knowledge"
        default_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created knowledge base directory at: {default_path}")
        return default_path

    def load_knowledge_base(self):
        """Load knowledge base with comprehensive error handling"""
        try:
            # Check cache first
            cached_kb = cache.get('knowledge_base_data')
            if cached_kb:
                self.knowledge_base = cached_kb['knowledge_base']
                self.probability_matrix = cached_kb['probability_matrix']
                self.diff_diagnosis = cached_kb['diff_diagnosis']
                self.symptoms_index = cached_kb['symptoms_index']
                logger.info("Knowledge base loaded from cache")
                return

            # Try to load from files
            self.knowledge_base = self.load_from_files()
            self.probability_matrix = self.load_probability_matrix()
            self.diff_diagnosis = self.load_differential_rules()
            self.symptoms_index = self.load_symptoms_index()

            if not self.knowledge_base:
                logger.warning("Knowledge base files not found, building from database")
                self.build_from_database()

            # Cache the loaded data
            cache_data = {
                'knowledge_base': self.knowledge_base,
                'probability_matrix': self.probability_matrix,
                'diff_diagnosis': self.diff_diagnosis,
                'symptoms_index': self.symptoms_index
            }
            cache.set('knowledge_base_data', cache_data, 60 * 30)  # Cache for 30 minutes

            logger.info("Knowledge base loaded successfully")

        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.build_fallback_data()

    def load_from_files(self):
        """Load knowledge base from JSON files"""
        try:
            kb_file = self.knowledge_base_dir / 'medical_knowledge_base.json'
            if kb_file.exists():
                with open(kb_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading knowledge base file: {e}")
        return None

    def load_probability_matrix(self):
        """Load probability matrix from file"""
        try:
            matrix_file = self.knowledge_base_dir / 'probability_matrix.json'
            if matrix_file.exists():
                with open(matrix_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading probability matrix: {e}")
        return {}

    def load_differential_rules(self):
        """Load differential diagnosis rules"""
        try:
            diff_file = self.knowledge_base_dir / 'differential_diagnosis.json'
            if diff_file.exists():
                with open(diff_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading differential rules: {e}")
        return {}

    def load_symptoms_index(self):
        """Load symptoms index from file"""
        try:
            symptoms_file = self.knowledge_base_dir / 'symptoms_index.json'
            if symptoms_file.exists():
                with open(symptoms_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading symptoms index: {e}")
        return {}

    def build_from_database(self):
        """Build knowledge base from database models"""
        try:
            logger.info("Building knowledge base from database...")

            # Get all conditions and symptoms from database
            conditions = MedicalCondition.objects.all()

            self.knowledge_base = {
                'metadata': {
                    'version': '2.0-db',
                    'source': 'database',
                    'conditions_count': conditions.count()
                },
                'conditions': {},
                'probability_matrix': {},
                'symptoms_index': {}
            }

            # Build conditions data
            for condition in conditions:
                condition_key = condition.name.lower().replace(' ', '_')

                # Get condition symptoms
                condition_symptoms = ConditionSymptom.objects.filter(condition=condition)
                symptoms_list = [cs.symptom.name for cs in condition_symptoms]

                self.knowledge_base['conditions'][condition_key] = {
                    'name': condition.name,
                    'description': condition.description,
                    'severity_level': condition.severity_level,
                    'symptoms': symptoms_list,
                    'sources': getattr(condition, 'source_websites', [])
                }

                # Build probability matrix
                self.knowledge_base['probability_matrix'][condition_key] = {}
                for cs in condition_symptoms:
                    symptom_name = cs.symptom.name.lower()
                    self.knowledge_base['probability_matrix'][condition_key][symptom_name] = cs.probability

                # Build symptoms index
                for cs in condition_symptoms:
                    symptom_name = cs.symptom.name.lower()
                    if symptom_name not in self.knowledge_base['symptoms_index']:
                        self.knowledge_base['symptoms_index'][symptom_name] = {
                            'frequency': 0,
                            'conditions': []
                        }
                    self.knowledge_base['symptoms_index'][symptom_name]['conditions'].append(condition_key)
                    self.knowledge_base['symptoms_index'][symptom_name]['frequency'] = cs.probability

            self.probability_matrix = self.knowledge_base['probability_matrix']
            self.symptoms_index = self.knowledge_base['symptoms_index']

            logger.info(f"Built knowledge base with {len(self.knowledge_base['conditions'])} conditions")

        except Exception as e:
            logger.error(f"Error building from database: {e}")
            self.build_fallback_data()

    def build_fallback_data(self):
        """Build minimal fallback data when all else fails"""
        logger.warning("Using fallback knowledge base data")

        self.knowledge_base = {
            'metadata': {
                'version': '1.0-fallback',
                'source': 'fallback'
            },
            'conditions': {
                'flu': {
                    'name': 'Influenza (Flu)',
                    'description': 'Viral respiratory illness',
                    'severity_level': 'MODERATE',
                    'symptoms': ['fever', 'body aches', 'fatigue', 'chills', 'headache']
                },
                'cold': {
                    'name': 'Common Cold',
                    'description': 'Viral upper respiratory infection',
                    'severity_level': 'MILD',
                    'symptoms': ['runny nose', 'sneezing', 'sore throat', 'congestion']
                },
                'covid-19': {
                    'name': 'COVID-19',
                    'description': 'Coronavirus disease',
                    'severity_level': 'MODERATE',
                    'symptoms': ['fever', 'cough', 'loss of taste', 'loss of smell', 'fatigue']
                },
                'allergy': {
                    'name': 'Allergic Reaction',
                    'description': 'Immune system response to allergens',
                    'severity_level': 'MILD',
                    'symptoms': ['sneezing', 'itchy eyes', 'runny nose', 'skin rash']
                }
            }
        }

        # Build basic probability matrix
        self.probability_matrix = {
            'flu': {'fever': 0.9, 'body aches': 0.8, 'fatigue': 0.8, 'chills': 0.7, 'headache': 0.6},
            'cold': {'runny nose': 0.8, 'sneezing': 0.7, 'sore throat': 0.6, 'congestion': 0.8},
            'covid-19': {'fever': 0.7, 'cough': 0.8, 'loss of taste': 0.6, 'loss of smell': 0.6, 'fatigue': 0.7},
            'allergy': {'sneezing': 0.9, 'itchy eyes': 0.8, 'runny nose': 0.7, 'skin rash': 0.5}
        }

        self.diff_diagnosis = {}
        self.symptoms_index = {}

    def analyze_symptoms_advanced(self, inputs: Dict) -> Dict:
        """
        Advanced symptom analysis using probability matrix and differential diagnosis
        """
        try:
            # Extract symptoms from inputs
            primary_symptoms = inputs.get('primary_symptoms', [])
            additional_symptoms = inputs.get('additional_symptoms', [])
            severity = inputs.get('severity', 5)
            duration = inputs.get('duration', '')
            differential_answer = inputs.get('differential_answer', '')

            # Combine all symptoms
            all_symptoms = primary_symptoms + additional_symptoms
            symptoms_text = ' '.join(all_symptoms).lower()

            # Calculate probabilities for each condition
            condition_scores = self.calculate_condition_probabilities(symptoms_text, severity, duration)

            # Apply differential diagnosis adjustments
            if differential_answer:
                condition_scores = self.apply_differential_scoring(condition_scores, differential_answer, inputs)

            # Sort conditions by probability
            sorted_conditions = sorted(condition_scores.items(), key=lambda x: x[1], reverse=True)

            if not sorted_conditions:
                return self.get_no_match_result()

            # Get top condition
            top_condition_key, confidence = sorted_conditions[0]
            top_condition = self.knowledge_base['conditions'][top_condition_key]

            # Get recommendations
            recommendations = self.get_recommendations(top_condition_key, confidence, severity)

            # Build result
            result = {
                'most_likely': {
                    'name': top_condition['name'],
                    'description': top_condition['description'],
                    'severity_level': top_condition['severity_level'],
                    'confidence': min(confidence, 1.0)
                },
                'all_matches': [
                    {
                        'name': self.knowledge_base['conditions'][cond_key]['name'],
                        'confidence': min(score, 1.0)
                    }
                    for cond_key, score in sorted_conditions[:3]
                ],
                'recommendations': recommendations,
                'next_steps': self.get_next_steps(top_condition_key, confidence, severity),
                'analysis_metadata': {
                    'symptoms_analyzed': len(all_symptoms),
                    'conditions_evaluated': len(condition_scores),
                    'knowledge_base_version': self.knowledge_base.get('metadata', {}).get('version', 'Unknown')
                }
            }

            return result

        except Exception as e:
            logger.error(f"Advanced analysis error: {e}")
            return self.get_fallback_analysis_result(inputs)

    def calculate_condition_probabilities(self, symptoms_text: str, severity: int, duration: str) -> Dict[str, float]:
        """Calculate probability scores for each condition"""
        condition_scores = {}

        for condition_key, condition_data in self.knowledge_base['conditions'].items():
            score = 0.0
            symptom_matches = 0

            # Get probability matrix for this condition
            condition_probabilities = self.probability_matrix.get(condition_key, {})

            # Score based on symptom matches
            for symptom in condition_data.get('symptoms', []):
                symptom_lower = symptom.lower()

                # Check for symptom presence in user input
                if symptom_lower in symptoms_text:
                    # Use probability from matrix if available
                    probability = condition_probabilities.get(symptom_lower, 0.3)
                    score += probability
                    symptom_matches += 1

                # Check for partial matches
                elif any(word in symptoms_text for word in symptom_lower.split()):
                    score += 0.2
                    symptom_matches += 0.5

            # Apply severity adjustments
            if severity >= 8:
                if condition_data.get('severity_level') in ['MODERATE', 'SEVERE']:
                    score += 0.2
            elif severity <= 3:
                if condition_data.get('severity_level') == 'MILD':
                    score += 0.1

            # Apply duration adjustments
            score = self.apply_duration_scoring(score, duration, condition_key)

            # Normalize score by number of condition symptoms
            total_symptoms = len(condition_data.get('symptoms', []))
            if total_symptoms > 0:
                score = score / total_symptoms * (1 + symptom_matches / total_symptoms)

            if score > 0:
                condition_scores[condition_key] = score

        return condition_scores

    def apply_duration_scoring(self, score: float, duration: str, condition_key: str) -> float:
        """Apply duration-based scoring adjustments"""
        duration_lower = duration.lower()

        # Duration-based adjustments for different conditions
        duration_adjustments = {
            'flu': {
                '1-3 days': 0.1,
                '4-7 days': 0.2,
                'more than a week': -0.1
            },
            'cold': {
                '4-7 days': 0.1,
                'more than a week': 0.2,
                'less than 24 hours': -0.1
            },
            'covid-19': {
                '1-3 days': 0.1,
                '4-7 days': 0.2,
                'more than a week': 0.1
            },
            'allergy': {
                'recurring episodes': 0.3,
                'more than a week': 0.2
            }
        }

        adjustments = duration_adjustments.get(condition_key, {})
        for duration_pattern, adjustment in adjustments.items():
            if duration_pattern in duration_lower:
                score += adjustment
                break

        return score

    def apply_differential_scoring(self, condition_scores: Dict[str, float], differential_answer: str, inputs: Dict) -> Dict[str, float]:
        """Apply differential diagnosis scoring based on specific questions"""
        # This would use the differential questions from chatbot_engine
        # For now, implement basic differential logic

        differential_answer_lower = differential_answer.lower()

        # Flu vs Cold differentiation
        if 'severe body aches' in differential_answer_lower:
            condition_scores['flu'] = condition_scores.get('flu', 0) + 0.3
            condition_scores['cold'] = condition_scores.get('cold', 0) - 0.1
        elif 'no body aches' in differential_answer_lower:
            condition_scores['cold'] = condition_scores.get('cold', 0) + 0.2
            condition_scores['flu'] = condition_scores.get('flu', 0) - 0.2

        # COVID vs Flu differentiation
        if 'complete loss' in differential_answer_lower and 'taste' in str(inputs):
            condition_scores['covid-19'] = condition_scores.get('covid-19', 0) + 0.4
            condition_scores['flu'] = condition_scores.get('flu', 0) - 0.2

        # Allergy vs Cold differentiation
        if 'seasonal pattern' in differential_answer_lower or 'environmental triggers' in differential_answer_lower:
            condition_scores['allergy'] = condition_scores.get('allergy', 0) + 0.3
            condition_scores['cold'] = condition_scores.get('cold', 0) - 0.2

        return condition_scores

    def get_recommendations(self, condition_key: str, confidence: float, severity: int) -> List[Dict]:
        """Get specialist recommendations based on condition and severity"""

        # Specialist mapping
        specialist_map = {
            'flu': 'General Practitioner',
            'cold': 'General Practitioner',
            'covid-19': 'Infectious Disease Specialist',
            'allergy': 'Allergist'
        }

        # Urgency determination
        if severity >= 8 or confidence >= 0.8:
            urgency = 'HIGH'
        elif severity >= 6 or confidence >= 0.6:
            urgency = 'MEDIUM'
        else:
            urgency = 'LOW'

        specialist = specialist_map.get(condition_key, 'General Practitioner')

        return [{
            'specialist': specialist,
            'urgency': urgency,
            'notes': self.get_condition_specific_notes(condition_key, severity),
            'confidence_level': confidence
        }]

    def get_condition_specific_notes(self, condition_key: str, severity: int) -> str:
        """Get condition-specific recommendations"""

        notes_map = {
            'flu': {
                'low': 'Rest, hydration, and over-the-counter medications for symptom relief.',
                'medium': 'Monitor symptoms closely. Consider antiviral medication if within 48 hours of onset.',
                'high': 'Seek medical attention promptly. High fever and severe symptoms may require prescription treatment.'
            },
            'cold': {
                'low': 'Rest, warm fluids, and supportive care. Symptoms typically resolve in 7-10 days.',
                'medium': 'Monitor symptoms. See doctor if symptoms worsen or persist beyond 10 days.',
                'high': 'Consult healthcare provider to rule out secondary infections.'
            },
            'covid-19': {
                'low': 'Isolate, monitor symptoms, and follow current health guidelines.',
                'medium': 'Consider testing and consult healthcare provider about treatment options.',
                'high': 'Seek immediate medical evaluation, especially if experiencing breathing difficulties.'
            },
            'allergy': {
                'low': 'Identify and avoid triggers. Consider over-the-counter antihistamines.',
                'medium': 'Consult allergist for comprehensive testing and treatment plan.',
                'high': 'Seek immediate care if experiencing severe allergic reactions.'
            }
        }

        severity_key = 'high' if severity >= 7 else 'medium' if severity >= 4 else 'low'
        return notes_map.get(condition_key, {}).get(severity_key, 'Consult healthcare provider for proper evaluation.')

    def get_next_steps(self, condition_key: str, confidence: float, severity: int) -> List[str]:
        """Get recommended next steps"""
        steps = []

        if severity >= 8:
            steps.append("Seek immediate medical attention")
        elif confidence >= 0.7:
            steps.append(f"Schedule appointment with recommended specialist")
        else:
            steps.append("Monitor symptoms for 24-48 hours")

        if condition_key == 'covid-19':
            steps.append("Consider COVID-19 testing")
            steps.append("Follow isolation guidelines")
        elif condition_key == 'flu':
            steps.append("Stay hydrated and get plenty of rest")
            steps.append("Consider antiviral medication if within 48 hours of symptom onset")
        elif condition_key == 'allergy':
            steps.append("Identify and avoid potential triggers")
            steps.append("Keep symptom diary for pattern identification")

        steps.append("Return for follow-up if symptoms worsen or persist")

        return steps[:4]  # Limit to 4 steps

    def get_no_match_result(self) -> Dict:
        """Return result when no conditions match"""
        return {
            'most_likely': {
                'name': 'Unable to determine',
                'description': 'Symptoms do not clearly match known conditions',
                'confidence': 0.0
            },
            'recommendations': [{
                'specialist': 'General Practitioner',
                'urgency': 'MEDIUM',
                'notes': 'Consult healthcare provider for comprehensive evaluation'
            }],
            'all_matches': [],
            'next_steps': [
                'Schedule appointment with healthcare provider',
                'Keep detailed symptom diary',
                'Monitor for symptom changes'
            ]
        }

    def get_fallback_analysis_result(self, inputs: Dict) -> Dict:
        """Fallback analysis result when main analysis fails"""
        severity = inputs.get('severity', 5)
        urgency = 'HIGH' if severity >= 8 else 'MEDIUM'

        return {
            'most_likely': {
                'name': 'Analysis unavailable',
                'description': 'Unable to complete symptom analysis',
                'confidence': 0.0
            },
            'recommendations': [{
                'specialist': 'General Practitioner',
                'urgency': urgency,
                'notes': 'Technical analysis unavailable. Please consult healthcare provider.'
            }],
            'all_matches': [],
            'next_steps': [
                'Consult healthcare provider for proper diagnosis',
                'Bring list of symptoms and their duration',
                'Mention any relevant medical history'
            ],
            'error_note': 'Analysis system temporarily unavailable'
        }