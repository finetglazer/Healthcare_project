# BE/medical/services/enhanced_analyzer.py
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from django.conf import settings
from ..models import MedicalCondition, Symptom, ConditionSymptom, SpecialistRecommendation

logger = logging.getLogger(__name__)

class EnhancedSymptomAnalyzer:  # Changed from FixedSymptomAnalyzer
    """
    Enhanced symptom analyzer with proper error handling and fallback mechanisms
    """

    def __init__(self):
        self.knowledge_base_dir = self.get_knowledge_base_path()
        self.load_knowledge_base()

    def get_knowledge_base_path(self):
        """Get knowledge base path with multiple fallback options"""
        possible_paths = [
            Path("medical_knowledge"),  # Relative to project root
            Path(settings.BASE_DIR) / "medical_knowledge",
            Path(settings.BASE_DIR) / "BE" / "medical_knowledge",
            Path("E:/PTTK/medical_knowledge"),  # Original absolute path
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
            # Try to load from files first
            self.knowledge_base = self.load_from_files()
            self.probability_matrix = self.load_probability_matrix()
            self.diff_diagnosis = self.load_differential_rules()

            if not self.knowledge_base:
                logger.warning("Knowledge base files not found, building from database")
                self.build_from_database()

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
        """Load probability matrix"""
        try:
            matrix_file = self.knowledge_base_dir / 'probability_matrix.json'
            if matrix_file.exists():
                with open(matrix_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading probability matrix: {e}")

        return self.build_matrix_from_db()

    def load_differential_rules(self):
        """Load differential diagnosis rules"""
        try:
            diff_file = self.knowledge_base_dir / 'differential_diagnosis.json'
            if diff_file.exists():
                with open(diff_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading differential rules: {e}")

        return self.get_default_diff_rules()

    def build_from_database(self):
        """Build knowledge base from Django database"""
        try:
            conditions = MedicalCondition.objects.all()

            self.knowledge_base = {
                'metadata': {
                    'version': '2.0',
                    'source': 'database',
                    'conditions_count': conditions.count()
                },
                'conditions': {}
            }

            for condition in conditions:
                condition_key = condition.name.lower().replace(' ', '-')

                # Get symptoms
                primary_symptoms = []
                secondary_symptoms = []

                condition_symptoms = ConditionSymptom.objects.filter(condition=condition)
                for cs in condition_symptoms:
                    symptom_data = {
                        'name': cs.symptom.name,
                        'probability': float(cs.probability),
                        'severity': ['mild', 'moderate', 'severe']  # Default
                    }

                    if cs.is_primary:
                        primary_symptoms.append(symptom_data)
                    else:
                        secondary_symptoms.append(symptom_data)

                self.knowledge_base['conditions'][condition_key] = {
                    'name': condition.name,
                    'description': condition.description,
                    'severity_level': condition.severity_level,
                    'primary_symptoms': primary_symptoms,
                    'secondary_symptoms': secondary_symptoms
                }

            self.probability_matrix = self.build_matrix_from_db()
            self.diff_diagnosis = self.get_default_diff_rules()

            logger.info("Knowledge base built from database")

        except Exception as e:
            logger.error(f"Error building from database: {e}")
            self.build_fallback_data()

    def build_matrix_from_db(self):
        """Build probability matrix from Django database"""
        matrix = {}

        try:
            conditions = MedicalCondition.objects.all()
            for condition in conditions:
                condition_key = condition.name.lower().replace(' ', '-')
                matrix[condition_key] = {}

                symptoms = ConditionSymptom.objects.filter(condition=condition)
                for cs in symptoms:
                    symptom_key = cs.symptom.name.lower()
                    matrix[condition_key][symptom_key] = {
                        'base_probability': float(cs.probability),
                        'is_primary': cs.is_primary,
                        'severity_modifier': {
                            'mild': 0.8,
                            'moderate': 1.0,
                            'severe': 1.2
                        }
                    }
        except Exception as e:
            logger.error(f"Error building matrix from database: {e}")
            matrix = self.get_fallback_matrix()

        return matrix

    def get_default_diff_rules(self):
        """Default differential diagnosis rules"""
        return {
            'distinguishing_features': {
                'flu_vs_cold': {
                    'flu_indicators': ['fever', 'body aches', 'fatigue'],
                    'cold_indicators': ['runny nose', 'sneezing'],
                    'confidence_threshold': 0.7
                },
                'covid_vs_flu': {
                    'covid_indicators': ['loss of taste', 'loss of smell'],
                    'flu_indicators': ['body aches', 'chills'],
                    'confidence_threshold': 0.6
                },
                'allergy_vs_cold': {
                    'allergy_indicators': ['itchy eyes', 'sneezing'],
                    'cold_indicators': ['sore throat', 'progression'],
                    'confidence_threshold': 0.8
                }
            },
            'combination_rules': {
                'high_confidence_flu': ['fever + body aches + fatigue'],
                'high_confidence_covid': ['loss of taste + loss of smell'],
                'high_confidence_allergy': ['itchy eyes + sneezing'],
                'high_confidence_cold': ['runny nose + sore throat']
            }
        }

    def get_fallback_matrix(self):
        """Fallback probability matrix if database is empty"""
        return {
            'flu': {
                'fever': {'base_probability': 0.9, 'is_primary': True, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}},
                'body aches': {'base_probability': 0.9, 'is_primary': True, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}},
                'fatigue': {'base_probability': 0.8, 'is_primary': False, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}},
                'headache': {'base_probability': 0.7, 'is_primary': False, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}}
            },
            'cold': {
                'runny nose': {'base_probability': 0.9, 'is_primary': True, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}},
                'sneezing': {'base_probability': 0.8, 'is_primary': True, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}},
                'sore throat': {'base_probability': 0.7, 'is_primary': False, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}}
            },
            'covid-19': {
                'loss of taste': {'base_probability': 0.8, 'is_primary': True, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}},
                'loss of smell': {'base_probability': 0.8, 'is_primary': True, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}},
                'persistent cough': {'base_probability': 0.7, 'is_primary': False, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}}
            },
            'allergy': {
                'sneezing': {'base_probability': 0.9, 'is_primary': True, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}},
                'itchy eyes': {'base_probability': 0.8, 'is_primary': True, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}},
                'watery eyes': {'base_probability': 0.8, 'is_primary': False, 'severity_modifier': {'mild': 0.8, 'moderate': 1.0, 'severe': 1.2}}
            }
        }

    def build_fallback_data(self):
        """Build minimal fallback data"""
        logger.warning("Using fallback data for symptom analysis")

        self.knowledge_base = {
            'metadata': {
                'version': '1.0',
                'source': 'fallback',
                'conditions_count': 4
            }
        }

        self.probability_matrix = self.get_fallback_matrix()
        self.diff_diagnosis = self.get_default_diff_rules()

    def analyze_symptoms_advanced(self, user_inputs: Dict) -> Dict:
        """
        Main analysis method with comprehensive error handling
        """
        try:
            # Validate inputs
            if not user_inputs:
                return self.get_empty_result()

            # Preprocess inputs
            processed_inputs = self.preprocess_inputs(user_inputs)

            if not processed_inputs.get('all_symptoms'):
                return self.get_empty_result()

            # Calculate scores
            base_scores = self.calculate_base_scores(processed_inputs)
            modified_scores = self.apply_modifiers(base_scores, processed_inputs)
            final_scores = self.apply_differential_diagnosis(modified_scores, processed_inputs)

            # Generate result
            result = self.build_analysis_result(final_scores, processed_inputs)

            return result

        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            return self.get_error_result(str(e))

    def preprocess_inputs(self, user_inputs: Dict) -> Dict:
        """Preprocess and normalize user inputs"""
        processed = {
            'all_symptoms': [],
            'severity': user_inputs.get('severity', 5),
            'duration': user_inputs.get('duration', ''),
            'age': user_inputs.get('age', 30)
        }

        # Combine symptoms
        primary = user_inputs.get('primary_symptoms', [])
        additional = user_inputs.get('additional_symptoms', [])

        # Handle different input formats
        if isinstance(primary, str):
            primary = [primary]
        if isinstance(additional, str):
            additional = [additional]

        # Normalize symptoms
        for symptom in primary + additional:
            if symptom and isinstance(symptom, str):
                normalized = self.normalize_symptom_name(symptom)
                if normalized:
                    processed['all_symptoms'].append({
                        'name': normalized,
                        'original': symptom,
                        'is_primary': symptom in primary
                    })

        return processed

    def normalize_symptom_name(self, symptom: str) -> str:
        """Normalize symptom names"""
        if not symptom:
            return ""

        # Clean input
        normalized = symptom.lower().strip()

        # Simple mapping for common variations
        mappings = {
            'high fever': 'fever',
            'body aches': 'body aches',
            'muscle pain': 'body aches',
            'runny nose': 'runny nose',
            'stuffy nose': 'congestion',
            'sore throat': 'sore throat',
            'loss of taste': 'loss of taste',
            'loss of smell': 'loss of smell',
            'shortness of breath': 'shortness of breath',
            'difficulty breathing': 'shortness of breath'
        }

        for key, value in mappings.items():
            if key in normalized:
                return value

        return normalized

    def calculate_base_scores(self, processed_inputs: Dict) -> Dict:
        """Calculate base probability scores"""
        scores = {condition: 0.0 for condition in self.probability_matrix.keys()}

        for symptom_data in processed_inputs['all_symptoms']:
            symptom_name = symptom_data['name']
            is_primary = symptom_data['is_primary']

            for condition in scores.keys():
                if condition in self.probability_matrix:
                    condition_symptoms = self.probability_matrix[condition]

                    if symptom_name in condition_symptoms:
                        symptom_info = condition_symptoms[symptom_name]
                        base_prob = symptom_info['base_probability']

                        if is_primary and symptom_info.get('is_primary', False):
                            base_prob *= 1.3

                        scores[condition] += base_prob

        return scores

    def apply_modifiers(self, base_scores: Dict, processed_inputs: Dict) -> Dict:
        """Apply severity and other modifiers"""
        modified_scores = base_scores.copy()
        severity = processed_inputs['severity']

        if severity >= 7:
            # Severe symptoms favor flu and COVID
            modified_scores['flu'] = modified_scores.get('flu', 0) * 1.2
            modified_scores['covid-19'] = modified_scores.get('covid-19', 0) * 1.1
        elif severity <= 3:
            # Mild symptoms favor cold and allergy
            modified_scores['cold'] = modified_scores.get('cold', 0) * 1.2
            modified_scores['allergy'] = modified_scores.get('allergy', 0) * 1.1

        return modified_scores

    def apply_differential_diagnosis(self, scores: Dict, processed_inputs: Dict) -> Dict:
        """Apply differential diagnosis rules"""
        # For now, just return scores as-is
        # You can enhance this with more sophisticated logic
        return scores

    def build_analysis_result(self, scores: Dict, processed_inputs: Dict) -> Dict:
        """Build final analysis result"""
        # Sort conditions by score
        sorted_conditions = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if not sorted_conditions or sorted_conditions[0][1] == 0:
            return self.get_empty_result()

        top_condition, top_score = sorted_conditions[0]

        # Calculate confidence
        max_possible = len(processed_inputs['all_symptoms']) * 1.5
        confidence = min(top_score / max_possible, 1.0) if max_possible > 0 else 0

        # Get recommendations
        recommendations = self.get_recommendations(top_condition, confidence, processed_inputs)

        return {
            'most_likely': {
                'condition': top_condition.replace('-', ' ').title(),
                'confidence': round(confidence, 3),
                'score': round(top_score, 3)
            },
            'all_conditions': [
                {
                    'condition': condition.replace('-', ' ').title(),
                    'confidence': round(min(score / max_possible, 1.0), 3) if max_possible > 0 else 0,
                    'score': round(score, 3)
                }
                for condition, score in sorted_conditions[:4]
            ],
            'recommendations': recommendations,
            'next_steps': self.generate_next_steps(top_condition, confidence, processed_inputs),
            'metadata': {
                'total_symptoms': len(processed_inputs['all_symptoms']),
                'severity_level': self.categorize_severity(processed_inputs['severity']),
                'analysis_version': '2.0-fixed'
            }
        }

    def get_recommendations(self, condition: str, confidence: float, processed_inputs: Dict) -> Dict:
        """Get medical recommendations"""
        # Default recommendations
        defaults = {
            'flu': {
                'specialist': 'General Practitioner',
                'urgency': 'MEDIUM',
                'notes': 'Rest, hydration, antiviral medication if needed'
            },
            'cold': {
                'specialist': 'General Practitioner',
                'urgency': 'LOW',
                'notes': 'Rest, hydration, symptom management'
            },
            'covid-19': {
                'specialist': 'General Practitioner',
                'urgency': 'HIGH',
                'notes': 'Get tested, isolate, monitor symptoms'
            },
            'allergy': {
                'specialist': 'Allergist',
                'urgency': 'LOW',
                'notes': 'Identify triggers, antihistamines'
            }
        }

        recommendation = defaults.get(condition, defaults['flu']).copy()

        # Adjust urgency based on severity
        if processed_inputs['severity'] >= 8:
            recommendation['urgency'] = 'HIGH'

        return recommendation

    def generate_next_steps(self, condition: str, confidence: float, processed_inputs: Dict) -> List[str]:
        """Generate next steps"""
        steps = []

        if confidence < 0.3:
            steps.append("Monitor symptoms for 24-48 hours")
            steps.append("Consider additional symptom assessment")

        if processed_inputs['severity'] >= 7:
            steps.append("Seek medical attention promptly")

        if condition == 'covid-19':
            steps.append("Get tested for COVID-19")
            steps.append("Isolate from others")
        elif condition == 'flu':
            steps.append("Rest and stay hydrated")
        elif condition == 'allergy':
            steps.append("Identify potential allergens")

        steps.append("Consult healthcare provider for proper diagnosis")

        return steps

    def categorize_severity(self, severity: int) -> str:
        """Categorize severity level"""
        if severity <= 3:
            return 'Mild'
        elif severity <= 6:
            return 'Moderate'
        else:
            return 'Severe'

    def get_empty_result(self) -> Dict:
        """Return empty result when no symptoms provided"""
        return {
            'most_likely': {
                'condition': 'Unknown',
                'confidence': 0.0,
                'score': 0.0
            },
            'all_conditions': [],
            'recommendations': {
                'specialist': 'General Practitioner',
                'urgency': 'MEDIUM',
                'notes': 'Please provide symptoms for analysis'
            },
            'next_steps': ['Describe your symptoms', 'Consult healthcare provider'],
            'metadata': {
                'total_symptoms': 0,
                'severity_level': 'Unknown',
                'analysis_version': '2.0-fixed'
            }
        }

    def get_error_result(self, error_msg: str) -> Dict:
        """Return error result"""
        return {
            'most_likely': {
                'condition': 'Analysis Error',
                'confidence': 0.0,
                'score': 0.0
            },
            'recommendations': {
                'specialist': 'General Practitioner',
                'urgency': 'MEDIUM',
                'notes': 'Analysis temporarily unavailable, please consult healthcare provider'
            },
            'error': error_msg,
            'next_steps': ['Consult healthcare provider directly'],
            'metadata': {
                'analysis_version': '2.0-fixed',
                'error': True
            }
        }