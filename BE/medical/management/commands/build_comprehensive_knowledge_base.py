# BE/medical/management/commands/build_medical_knowledge.py
# Fixed version with error handling and fallback mechanisms

import json
import logging
import time
from pathlib import Path
from django.core.management.base import BaseCommand
from ...models import MedicalCondition, Symptom, ConditionSymptom, SpecialistRecommendation

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Build medical knowledge base with proper error handling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use-fallback',
            action='store_true',
            help='Use fallback data instead of web scraping'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='medical_knowledge',
            help='Output directory for knowledge base files'
        )

    def handle(self, *args, **options):
        self.stdout.write('Building medical knowledge base...')

        try:
            if options['use_fallback']:
                self.build_fallback_knowledge_base(options['output_dir'])
            else:
                self.build_comprehensive_knowledge_base(options['output_dir'])

            self.stdout.write(
                self.style.SUCCESS('Successfully built medical knowledge base!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error building knowledge base: {e}')
            )
            # Fallback to basic data
            self.build_fallback_knowledge_base(options['output_dir'])

    def build_fallback_knowledge_base(self, output_dir):
        """Build knowledge base using predefined data (no web scraping)"""
        self.stdout.write('Building fallback knowledge base...')

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Define comprehensive medical data
        medical_data = {
            'flu': {
                'name': 'Influenza (Flu)',
                'description': 'Viral respiratory illness caused by influenza viruses',
                'severity_level': 'MODERATE',
                'primary_symptoms': [
                    {'name': 'High Fever', 'probability': 0.9, 'severity': ['moderate', 'severe']},
                    {'name': 'Body Aches', 'probability': 0.9, 'severity': ['moderate', 'severe']},
                    {'name': 'Fatigue', 'probability': 0.8, 'severity': ['moderate', 'severe']},
                    {'name': 'Chills', 'probability': 0.8, 'severity': ['moderate', 'severe']},
                    {'name': 'Headache', 'probability': 0.7, 'severity': ['moderate', 'severe']}
                ],
                'secondary_symptoms': [
                    {'name': 'Dry Cough', 'probability': 0.6, 'severity': ['mild', 'moderate']},
                    {'name': 'Sore Throat', 'probability': 0.5, 'severity': ['mild', 'moderate']},
                    {'name': 'Runny Nose', 'probability': 0.4, 'severity': ['mild']}
                ],
                'specialist': 'General Practitioner',
                'urgency': 'MEDIUM',
                'notes': 'Rest, hydration, antiviral medication if needed'
            },
            'cold': {
                'name': 'Common Cold',
                'description': 'Viral upper respiratory tract infection',
                'severity_level': 'MILD',
                'primary_symptoms': [
                    {'name': 'Runny Nose', 'probability': 0.9, 'severity': ['mild', 'moderate']},
                    {'name': 'Sneezing', 'probability': 0.8, 'severity': ['mild', 'moderate']},
                    {'name': 'Sore Throat', 'probability': 0.7, 'severity': ['mild', 'moderate']},
                    {'name': 'Congestion', 'probability': 0.8, 'severity': ['mild', 'moderate']}
                ],
                'secondary_symptoms': [
                    {'name': 'Mild Cough', 'probability': 0.6, 'severity': ['mild']},
                    {'name': 'Low Grade Fever', 'probability': 0.3, 'severity': ['mild']},
                    {'name': 'Mild Fatigue', 'probability': 0.4, 'severity': ['mild']}
                ],
                'specialist': 'General Practitioner',
                'urgency': 'LOW',
                'notes': 'Rest, hydration, symptom management'
            },
            'covid-19': {
                'name': 'COVID-19',
                'description': 'Coronavirus disease caused by SARS-CoV-2',
                'severity_level': 'MODERATE',
                'primary_symptoms': [
                    {'name': 'Loss of Taste', 'probability': 0.8, 'severity': ['moderate', 'severe']},
                    {'name': 'Loss of Smell', 'probability': 0.8, 'severity': ['moderate', 'severe']},
                    {'name': 'Persistent Cough', 'probability': 0.7, 'severity': ['moderate', 'severe']},
                    {'name': 'Fever', 'probability': 0.7, 'severity': ['moderate', 'severe']}
                ],
                'secondary_symptoms': [
                    {'name': 'Fatigue', 'probability': 0.6, 'severity': ['moderate', 'severe']},
                    {'name': 'Shortness of Breath', 'probability': 0.5, 'severity': ['moderate', 'severe']},
                    {'name': 'Sore Throat', 'probability': 0.4, 'severity': ['mild', 'moderate']},
                    {'name': 'Headache', 'probability': 0.4, 'severity': ['mild', 'moderate']}
                ],
                'specialist': 'General Practitioner',
                'urgency': 'HIGH',
                'notes': 'Get tested, isolate, monitor symptoms closely'
            },
            'allergy': {
                'name': 'Allergic Reaction',
                'description': 'Immune system response to allergens',
                'severity_level': 'MILD',
                'primary_symptoms': [
                    {'name': 'Sneezing', 'probability': 0.9, 'severity': ['mild', 'moderate']},
                    {'name': 'Itchy Eyes', 'probability': 0.8, 'severity': ['mild', 'moderate']},
                    {'name': 'Watery Eyes', 'probability': 0.8, 'severity': ['mild', 'moderate']},
                    {'name': 'Clear Runny Nose', 'probability': 0.8, 'severity': ['mild', 'moderate']}
                ],
                'secondary_symptoms': [
                    {'name': 'Itchy Throat', 'probability': 0.6, 'severity': ['mild']},
                    {'name': 'Skin Rash', 'probability': 0.4, 'severity': ['mild', 'moderate']},
                    {'name': 'Congestion', 'probability': 0.5, 'severity': ['mild', 'moderate']}
                ],
                'specialist': 'Allergist',
                'urgency': 'LOW',
                'notes': 'Identify triggers, antihistamines, avoid allergens'
            }
        }

        # Build knowledge base structure
        knowledge_base = {
            'metadata': {
                'version': '2.0',
                'created': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'fallback_data',
                'conditions_count': len(medical_data)
            },
            'conditions': medical_data,
            'probability_matrix': self.build_probability_matrix(medical_data),
            'differential_diagnosis': self.build_differential_rules(),
            'symptoms_index': self.build_symptoms_index(medical_data)
        }

        # Save files
        self.save_knowledge_base(knowledge_base, output_path)

        # Populate Django database
        self.populate_database(medical_data)

        self.stdout.write('Fallback knowledge base created successfully!')

    def build_probability_matrix(self, medical_data):
        """Build probability matrix from medical data"""
        matrix = {}

        for condition_key, condition_data in medical_data.items():
            matrix[condition_key] = {}

            # Process primary symptoms
            for symptom in condition_data.get('primary_symptoms', []):
                matrix[condition_key][symptom['name'].lower()] = {
                    'base_probability': symptom['probability'],
                    'is_primary': True,
                    'severity_modifier': {
                        'mild': 0.8,
                        'moderate': 1.0,
                        'severe': 1.2
                    }
                }

            # Process secondary symptoms
            for symptom in condition_data.get('secondary_symptoms', []):
                matrix[condition_key][symptom['name'].lower()] = {
                    'base_probability': symptom['probability'],
                    'is_primary': False,
                    'severity_modifier': {
                        'mild': 0.9,
                        'moderate': 1.0,
                        'severe': 1.1
                    }
                }

        return matrix

    def build_differential_rules(self):
        """Build differential diagnosis rules"""
        return {
            'distinguishing_features': {
                'flu_vs_cold': {
                    'flu_indicators': ['high fever', 'body aches', 'severe fatigue'],
                    'cold_indicators': ['runny nose', 'sneezing', 'mild symptoms'],
                    'confidence_threshold': 0.7
                },
                'covid_vs_flu': {
                    'covid_indicators': ['loss of taste', 'loss of smell', 'persistent cough'],
                    'flu_indicators': ['body aches', 'chills', 'rapid onset'],
                    'confidence_threshold': 0.6
                },
                'allergy_vs_cold': {
                    'allergy_indicators': ['itchy eyes', 'sneezing', 'clear discharge'],
                    'cold_indicators': ['sore throat', 'progression', 'thick discharge'],
                    'confidence_threshold': 0.8
                }
            },
            'combination_rules': {
                'high_confidence_flu': ['fever + body aches + fatigue'],
                'high_confidence_covid': ['loss of taste + loss of smell'],
                'high_confidence_allergy': ['itchy eyes + sneezing + clear runny nose'],
                'high_confidence_cold': ['runny nose + sore throat + sneezing']
            }
        }

    def build_symptoms_index(self, medical_data):
        """Build searchable symptoms index"""
        index = {}

        for condition_key, condition_data in medical_data.items():
            for category in ['primary_symptoms', 'secondary_symptoms']:
                for symptom in condition_data.get(category, []):
                    symptom_name = symptom['name'].lower()

                    if symptom_name not in index:
                        index[symptom_name] = {
                            'conditions': {},
                            'category': 'primary' if 'primary' in category else 'secondary'
                        }

                    index[symptom_name]['conditions'][condition_key] = {
                        'probability': symptom['probability'],
                        'severity': symptom['severity']
                    }

        return index

    def save_knowledge_base(self, knowledge_base, output_path):
        """Save knowledge base to files"""
        try:
            # Main knowledge base
            with open(output_path / 'medical_knowledge_base.json', 'w', encoding='utf-8') as f:
                json.dump(knowledge_base, f, indent=2, ensure_ascii=False)

            # Probability matrix
            with open(output_path / 'probability_matrix.json', 'w', encoding='utf-8') as f:
                json.dump(knowledge_base['probability_matrix'], f, indent=2)

            # Symptoms index
            with open(output_path / 'symptoms_index.json', 'w', encoding='utf-8') as f:
                json.dump(knowledge_base['symptoms_index'], f, indent=2)

            # Differential diagnosis
            with open(output_path / 'differential_diagnosis.json', 'w', encoding='utf-8') as f:
                json.dump(knowledge_base['differential_diagnosis'], f, indent=2)

            self.stdout.write(f'Knowledge base files saved to {output_path}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error saving files: {e}'))

    def populate_database(self, medical_data):
        """Populate Django database with medical data"""
        try:
            self.stdout.write('Populating database...')

            for condition_key, condition_data in medical_data.items():
                # Create condition
                condition, created = MedicalCondition.objects.get_or_create(
                    name=condition_data['name'],
                    defaults={
                        'description': condition_data['description'],
                        'severity_level': condition_data['severity_level'],
                        'recommended_action': condition_data['notes'],
                        'source_websites': []
                    }
                )

                if created:
                    self.stdout.write(f'Created condition: {condition.name}')

                # Process symptoms
                for category in ['primary_symptoms', 'secondary_symptoms']:
                    for symptom_data in condition_data.get(category, []):
                        # Create symptom
                        symptom, created = Symptom.objects.get_or_create(
                            name=symptom_data['name'],
                            defaults={
                                'description': f"Symptom: {symptom_data['name']}",
                                'is_common': category == 'primary_symptoms'
                            }
                        )

                        # Create relationship
                        ConditionSymptom.objects.get_or_create(
                            condition=condition,
                            symptom=symptom,
                            defaults={
                                'probability': symptom_data['probability'],
                                'is_primary': category == 'primary_symptoms'
                            }
                        )

                # Create specialist recommendation
                SpecialistRecommendation.objects.get_or_create(
                    condition=condition,
                    specialist_type=condition_data['specialist'],
                    defaults={
                        'urgency_level': condition_data['urgency'],
                        'notes': condition_data['notes']
                    }
                )

            self.stdout.write('Database populated successfully!')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error populating database: {e}'))

    def build_comprehensive_knowledge_base(self, output_dir):
        """Build knowledge base with web scraping (if needed)"""
        self.stdout.write('Comprehensive building not available, using fallback...')
        self.build_fallback_knowledge_base(output_dir)