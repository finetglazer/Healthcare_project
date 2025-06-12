# BE/medical/services/enhanced_analyzer.py
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from django.conf import settings
from ..models import MedicalCondition, Symptom, ConditionSymptom, SpecialistRecommendation
import math
import re

logger = logging.getLogger(__name__)

class EnhancedSymptomAnalyzer:
    """
    Advanced symptom analysis engine using comprehensive knowledge base
    """

    def __init__(self):
        self.knowledge_base_dir = Path("E:/PTTK/medical_knowledge")
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Load knowledge base from files"""
        try:
            # Load main knowledge base
            kb_file = self.knowledge_base_dir / 'medical_knowledge_base.json'
            if kb_file.exists():
                with open(kb_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
            else:
                logger.warning("Knowledge base file not found, using database only")
                self.knowledge_base = None

            # Load probability matrix
            matrix_file = self.knowledge_base_dir / 'probability_matrix.json'
            if matrix_file.exists():
                with open(matrix_file, 'r', encoding='utf-8') as f:
                    self.probability_matrix = json.load(f)
            else:
                self.probability_matrix = self.build_matrix_from_db()

            # Load differential diagnosis rules
            diff_file = self.knowledge_base_dir / 'differential_diagnosis.json'
            if diff_file.exists():
                with open(diff_file, 'r', encoding='utf-8') as f:
                    self.diff_diagnosis = json.load(f)
            else:
                self.diff_diagnosis = self.get_default_diff_rules()

            logger.info("Knowledge base loaded successfully")

        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.build_fallback_data()

    def build_matrix_from_db(self):
        """Build probability matrix from Django database"""
        matrix = {}

        conditions = MedicalCondition.objects.all()
        for condition in conditions:
            condition_key = condition.name.lower().replace(' ', '-')
            matrix[condition_key] = {}

            symptoms = ConditionSymptom.objects.filter(condition=condition)
            for cs in symptoms:
                symptom_key = cs.symptom.name.lower()
                matrix[condition_key][symptom_key] = {
                    'base_probability': cs.probability,
                    'is_primary': cs.is_primary,
                    'severity_modifier': {
                        'mild': 0.8,
                        'moderate': 1.0,
                        'severe': 1.2
                    }
                }

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
                }
            }
        }

    def build_fallback_data(self):
        """Build fallback data if knowledge base fails to load"""
        self.knowledge_base = None
        self.probability_matrix = self.build_matrix_from_db()
        self.diff_diagnosis = self.get_default_diff_rules()

    def analyze_symptoms_advanced(self, user_inputs: Dict) -> Dict:
        """
        Advanced symptom analysis with enhanced logic

        Args:
            user_inputs: {
                'primary_symptoms': List[str],
                'severity': int (1-10),
                'duration': str,
                'additional_symptoms': List[str],
                'age': int (optional),
                'medical_history': List[str] (optional)
            }

        Returns:
            Comprehensive analysis results
        """
        try:
            # Preprocess inputs
            processed_inputs = self.preprocess_inputs(user_inputs)

            # Calculate base probabilities
            base_scores = self.calculate_base_scores(processed_inputs)

            # Apply modifiers
            modified_scores = self.apply_modifiers(base_scores, processed_inputs)

            # Apply differential diagnosis
            final_scores = self.apply_differential_diagnosis(modified_scores, processed_inputs)

            # Generate recommendations
            recommendations = self.generate_recommendations(final_scores, processed_inputs)

            # Build comprehensive result
            result = self.build_analysis_result(final_scores, recommendations, processed_inputs)

            return result

        except Exception as e:
            logger.error(f"Error in advanced symptom analysis: {e}")
            return self.fallback_analysis(user_inputs)

    def preprocess_inputs(self, user_inputs: Dict) -> Dict:
        """Preprocess and normalize user inputs"""
        processed = {
            'all_symptoms': [],
            'severity': user_inputs.get('severity', 5),
            'duration': user_inputs.get('duration', ''),
            'age': user_inputs.get('age', 30),
            'medical_history': user_inputs.get('medical_history', [])
        }

        # Combine all symptoms
        primary = user_inputs.get('primary_symptoms', [])
        additional = user_inputs.get('additional_symptoms', [])

        # Normalize symptom names
        for symptom in primary + additional:
            normalized = self.normalize_symptom_name(symptom)
            if normalized:
                processed['all_symptoms'].append({
                    'name': normalized,
                    'original': symptom,
                    'is_primary': symptom in primary
                })

        return processed

    def normalize_symptom_name(self, symptom: str) -> str:
        """Normalize symptom names for matching"""
        if not symptom:
            return ""

        # Convert to lowercase and clean
        normalized = symptom.lower().strip()

        # Common replacements
        replacements = {
            'runny nose': 'runny nose',
            'stuffy nose': 'congestion',
            'blocked nose': 'congestion',
            'sore throat': 'sore throat',
            'throat pain': 'sore throat',
            'body aches': 'body aches',
            'muscle pain': 'body aches',
            'headache': 'headache',
            'head pain': 'headache',
            'fever': 'fever',
            'high temperature': 'fever',
            'cough': 'cough',
            'coughing': 'cough',
            'fatigue': 'fatigue',
            'tiredness': 'fatigue',
            'tired': 'fatigue',
            'sneezing': 'sneezing',
            'loss of taste': 'loss of taste',
            'loss of smell': 'loss of smell',
            'shortness of breath': 'shortness of breath',
            'difficulty breathing': 'shortness of breath',
            'itchy eyes': 'itchy eyes',
            'watery eyes': 'watery eyes'
        }

        # Apply replacements
        for key, value in replacements.items():
            if key in normalized:
                return value

        # Fuzzy matching for partial matches
        for key, value in replacements.items():
            if self.fuzzy_match(normalized, key):
                return value

        return normalized

    def fuzzy_match(self, text: str, target: str, threshold: float = 0.7) -> bool:
        """Simple fuzzy matching"""
        if not text or not target:
            return False

        # Check if most words match
        text_words = set(text.split())
        target_words = set(target.split())

        if not target_words:
            return False

        intersection = text_words.intersection(target_words)
        similarity = len(intersection) / len(target_words)

        return similarity >= threshold

    def calculate_base_scores(self, processed_inputs: Dict) -> Dict:
        """Calculate base probability scores for each condition"""
        scores = {
            'flu': 0.0,
            'cold': 0.0,
            'covid-19': 0.0,
            'allergy': 0.0
        }

        for symptom_data in processed_inputs['all_symptoms']:
            symptom_name = symptom_data['name']
            is_primary = symptom_data['is_primary']

            # Check each condition
            for condition in scores.keys():
                if condition in self.probability_matrix:
                    condition_symptoms = self.probability_matrix[condition]

                    if symptom_name in condition_symptoms:
                        symptom_info = condition_symptoms[symptom_name]
                        base_prob = symptom_info['base_probability']

                        # Boost for primary symptoms reported as primary
                        if is_primary and symptom_info.get('is_primary', False):
                            base_prob *= 1.3

                        scores[condition] += base_prob

        return scores

    def apply_modifiers(self, base_scores: Dict, processed_inputs: Dict) -> Dict:
        """Apply severity, duration, and other modifiers"""
        modified_scores = base_scores.copy()

        severity = processed_inputs['severity']
        duration = processed_inputs['duration'].lower()
        age = processed_inputs['age']

        # Severity modifiers
        severity_modifier = {
            'mild': (1, 3): 0.8,
        'moderate': (4, 6): 1.0,
        'severe': (7, 10): 1.2
        }

        for level, (min_sev, max_sev) in severity_modifier.items():
            if min_sev <= severity <= max_sev:
                if level == 'severe':
                    # Severe symptoms more likely for flu and COVID
                    modified_scores['flu'] *= 1.2
                    modified_scores['covid-19'] *= 1.1
                elif level == 'mild':
                    # Mild symptoms more likely for cold and allergy
                    modified_scores['cold'] *= 1.2
                    modified_scores['allergy'] *= 1.1
                break

        # Duration modifiers
        if 'sudden' in duration or 'rapid' in duration:
            modified_scores['flu'] *= 1.3  # Flu has rapid onset
        elif 'gradual' in duration or 'slow' in duration:
            modified_scores['cold'] *= 1.2  # Cold has gradual onset
        elif 'persistent' in duration or 'long' in duration:
            modified_scores['covid-19'] *= 1.2  # COVID can be persistent

        # Age modifiers
        if age > 65:
            modified_scores['flu'] *= 1.1
            modified_scores['covid-19'] *= 1.1
        elif age < 18:
            modified_scores['cold'] *= 1.1
            modified_scores['allergy'] *= 1.1

        return modified_scores

    def apply_differential_diagnosis(self, scores: Dict, processed_inputs: Dict) -> Dict:
        """Apply differential diagnosis rules"""
        final_scores = scores.copy()

        symptom_names = [s['name'] for s in processed_inputs['all_symptoms']]

        # Apply distinguishing features
        distinguishing = self.diff_diagnosis.get('distinguishing_features', {})

        for comparison, rules in distinguishing.items():
            if comparison == 'flu_vs_cold':
                flu_indicators = rules['flu_indicators']
                cold_indicators = rules['cold_indicators']

                flu_matches = sum(1 for indicator in flu_indicators
                                  if any(indicator in symptom for symptom in symptom_names))
                cold_matches = sum(1 for indicator in cold_indicators
                                   if any(indicator in symptom for symptom in symptom_names))

                if flu_matches > cold_matches:
                    final_scores['flu'] *= 1.2
                    final_scores['cold'] *= 0.8
                elif cold_matches > flu_matches:
                    final_scores['cold'] *= 1.2
                    final_scores['flu'] *= 0.8

        # Apply combination rules
        combination_rules = self.diff_diagnosis.get('combination_rules', {})

        for rule_name, required_symptoms in combination_rules.items():
            for symptom_combo in required_symptoms:
                symptoms_in_combo = symptom_combo.split(' + ')
                matches = sum(1 for req_symptom in symptoms_in_combo
                              if any(req_symptom.lower() in symptom.lower()
                                     for symptom in symptom_names))

                if matches == len(symptoms_in_combo):
                    if 'flu' in rule_name:
                        final_scores['flu'] *= 1.4
                    elif 'covid' in rule_name:
                        final_scores['covid-19'] *= 1.4
                    elif 'allergy' in rule_name:
                        final_scores['allergy'] *= 1.4
                    elif 'cold' in rule_name:
                        final_scores['cold'] *= 1.4

        return final_scores

    def generate_recommendations(self, scores: Dict, processed_inputs: Dict) -> Dict:
        """Generate medical recommendations"""
        # Get top condition
        top_condition = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[top_condition]

        # Normalize confidence to 0-1 scale
        max_possible_score = len(processed_inputs['all_symptoms']) * 1.5
        normalized_confidence = min(confidence / max_possible_score, 1.0) if max_possible_score > 0 else 0

        # Get recommendations from database
        try:
            condition_obj = MedicalCondition.objects.get(name__icontains=top_condition.replace('-', ' '))
            specialist_rec = SpecialistRecommendation.objects.filter(condition=condition_obj).first()

            if specialist_rec:
                recommendations = {
                    'specialist': specialist_rec.specialist_type,
                    'urgency': specialist_rec.urgency_level,
                    'notes': specialist_rec.notes
                }
            else:
                recommendations = self.get_default_recommendations(top_condition)
        except:
            recommendations = self.get_default_recommendations(top_condition)

        # Adjust urgency based on severity and symptoms
        severity = processed_inputs['severity']
        if severity >= 8:
            recommendations['urgency'] = 'HIGH'
        elif 'shortness of breath' in [s['name'] for s in processed_inputs['all_symptoms']]:
            recommendations['urgency'] = 'HIGH'

        return recommendations

    def get_default_recommendations(self, condition: str) -> Dict:
        """Default recommendations for conditions"""
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
                'notes': 'Get tested, isolate, monitor symptoms closely'
            },
            'allergy': {
                'specialist': 'Allergist',
                'urgency': 'LOW',
                'notes': 'Identify triggers, antihistamines, avoid allergens'
            }
        }
        return defaults.get(condition, defaults['flu'])

    def build_analysis_result(self, scores: Dict, recommendations: Dict, processed_inputs: Dict) -> Dict:
        """Build comprehensive analysis result"""
        # Sort conditions by score
        sorted_conditions = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Calculate confidence
        top_score = sorted_conditions[0][1] if sorted_conditions else 0
        max_possible = len(processed_inputs['all_symptoms']) * 1.5
        confidence = min(top_score / max_possible, 1.0) if max_possible > 0 else 0

        # Build result
        result = {
            'most_likely': {
                'condition': sorted_conditions[0][0].replace('-', ' ').title() if sorted_conditions else 'Unknown',
                'confidence': round(confidence, 3),
                'score': round(top_score, 3)
            },
            'all_conditions': [
                {
                    'condition': condition.replace('-', ' ').title(),
                    'confidence': round(min(score / max_possible, 1.0), 3) if max_possible > 0 else 0,
                    'score': round(score, 3)
                }
                for condition, score in sorted_conditions
            ],
            'recommendations': recommendations,
            'symptoms_analysis': self.analyze_symptom_patterns(processed_inputs),
            'next_steps': self.generate_next_steps(sorted_conditions[0][0] if sorted_conditions else 'unknown',
                                                   confidence, processed_inputs),
            'metadata': {
                'total_symptoms': len(processed_inputs['all_symptoms']),
                'severity_level': self.categorize_severity(processed_inputs['severity']),
                'analysis_version': '2.0'
            }
        }

        return result

    def analyze_symptom_patterns(self, processed_inputs: Dict) -> Dict:
        """Analyze symptom patterns and combinations"""
        symptoms = [s['name'] for s in processed_inputs['all_symptoms']]

        patterns = {
            'respiratory_cluster': ['cough', 'sore throat', 'runny nose', 'congestion'],
            'systemic_cluster': ['fever', 'fatigue', 'body aches', 'headache'],
            'allergic_cluster': ['sneezing', 'itchy eyes', 'watery eyes'],
            'covid_specific': ['loss of taste', 'loss of smell']
        }

        pattern_analysis = {}
        for pattern_name, pattern_symptoms in patterns.items():
            matches = sum(1 for ps in pattern_symptoms if ps in symptoms)
            pattern_analysis[pattern_name] = {
                'matches': matches,
                'total': len(pattern_symptoms),
                'percentage': round(matches / len(pattern_symptoms) * 100, 1)
            }

        return pattern_analysis

    def categorize_severity(self, severity: int) -> str:
        """Categorize severity level"""
        if severity <= 3:
            return 'Mild'
        elif severity <= 6:
            return 'Moderate'
        else:
            return 'Severe'

    def generate_next_steps(self, top_condition: str, confidence: float, processed_inputs: Dict) -> List[str]:
        """Generate next steps based on analysis"""
        steps = []

        if confidence < 0.3:
            steps.append("Consider additional symptom assessment")
            steps.append("Monitor symptoms for 24-48 hours")

        if processed_inputs['severity'] >= 7:
            steps.append("Seek medical attention promptly")

        if top_condition == 'covid-19':
            steps.append("Get tested for COVID-19")
            steps.append("Isolate from others")
        elif top_condition == 'flu':
            steps.append("Rest and stay hydrated")
            steps.append("Consider antiviral medication if within 48 hours of onset")
        elif top_condition == 'allergy':
            steps.append("Identify and avoid potential allergens")
            steps.append("Consider antihistamines")

        steps.append("Consult with healthcare provider for proper diagnosis")

        return steps

    def fallback_analysis(self, user_inputs: Dict) -> Dict:
        """Fallback analysis if main analysis fails"""
        return {
            'most_likely': {
                'condition': 'Unknown',
                'confidence': 0.0,
                'score': 0.0
            },
            'recommendations': {
                'specialist': 'General Practitioner',
                'urgency': 'MEDIUM',
                'notes': 'Please consult a healthcare provider for proper evaluation'
            },
            'error': 'Analysis engine temporarily unavailable'
        }