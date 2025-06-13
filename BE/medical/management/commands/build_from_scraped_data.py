# BE/medical/management/commands/build_from_scraped_data.py
import json
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from ...models import MedicalCondition, Symptom, ConditionSymptom, SpecialistRecommendation

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Build knowledge base from scraped medical data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scraped-file',
            type=str,
            help='Specific scraped data file to use',
            default='scraped_medical_data.json'
        )

    def handle(self, *args, **options):
        self.stdout.write('Building knowledge base from scraped data...')

        # Find scraped data file
        knowledge_dir = Path(settings.BASE_DIR) / "medical_knowledge"
        scraped_file = knowledge_dir / options['scraped_file']

        if not scraped_file.exists():
            # Try to find the latest timestamped file
            scraped_files = list(knowledge_dir.glob('scraped_medical_data_*.json'))
            if scraped_files:
                scraped_file = max(scraped_files, key=lambda x: x.stat().st_mtime)
                self.stdout.write(f'Using latest scraped file: {scraped_file.name}')
            else:
                self.stdout.write(self.style.ERROR('No scraped data files found!'))
                return

        try:
            # Load scraped data
            with open(scraped_file, 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)

            # Build knowledge base from scraped data
            knowledge_base = self.build_knowledge_base_from_scraped(scraped_data)

            # Save new knowledge base files
            self.save_knowledge_base_files(knowledge_base, knowledge_dir)

            self.stdout.write(
                self.style.SUCCESS('Successfully built knowledge base from scraped data!')
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

    def build_knowledge_base_from_scraped(self, scraped_data):
        """Build knowledge base structure from scraped data"""

        knowledge_base = {
            'metadata': {
                'version': '2.0-scraped',
                'source': 'web_scraped',
                'conditions_count': len(scraped_data),
                'created': str(timezone.now())
            },
            'conditions': {},
            'probability_matrix': {},
            'symptoms_index': {}
        }

        # Process each condition
        for condition_key, condition_data in scraped_data.items():
            # Convert scraped data to knowledge base format
            processed_condition = {
                'name': condition_data['name'],
                'description': ' '.join(condition_data['descriptions'][:2]) if condition_data['descriptions'] else f"Information about {condition_data['name']}",
                'severity_level': self.determine_severity(condition_key),
                'sources': condition_data['sources'],
                'symptoms': condition_data['symptoms']
            }

            knowledge_base['conditions'][condition_key] = processed_condition

            # Build probability matrix for this condition
            knowledge_base['probability_matrix'][condition_key] = {}

            for i, symptom in enumerate(condition_data['symptoms']):
                clean_symptom = symptom.lower().strip()

                # Assign probabilities based on position and content
                if i < 3:  # First 3 symptoms are usually most important
                    base_prob = 0.8
                    is_primary = True
                elif i < 6:
                    base_prob = 0.6
                    is_primary = False
                else:
                    base_prob = 0.4
                    is_primary = False

                # Boost probability for key symptoms
                if self.is_key_symptom(clean_symptom, condition_key):
                    base_prob = min(base_prob + 0.2, 1.0)
                    is_primary = True

                knowledge_base['probability_matrix'][condition_key][clean_symptom] = {
                    'base_probability': base_prob,
                    'is_primary': is_primary,
                    'severity_modifier': {
                        'mild': 0.8,
                        'moderate': 1.0,
                        'severe': 1.2
                    }
                }

            # Build symptoms index
            for symptom in condition_data['symptoms']:
                clean_symptom = symptom.lower().strip()

                if clean_symptom not in knowledge_base['symptoms_index']:
                    knowledge_base['symptoms_index'][clean_symptom] = {
                        'conditions': {},
                        'category': 'primary' if self.is_key_symptom(clean_symptom, condition_key) else 'secondary'
                    }

                knowledge_base['symptoms_index'][clean_symptom]['conditions'][condition_key] = {
                    'probability': knowledge_base['probability_matrix'][condition_key][clean_symptom]['base_probability'],
                    'severity': ['mild', 'moderate', 'severe']
                }

        return knowledge_base

    def is_key_symptom(self, symptom, condition):
        """Determine if symptom is key for condition"""
        key_symptoms = {
            'flu': ['fever', 'body aches', 'fatigue', 'chills', 'muscle aches'],
            'cold': ['runny nose', 'sneezing', 'sore throat', 'congestion'],
            'covid-19': ['loss of taste', 'loss of smell', 'cough', 'fever', 'shortness of breath'],
            'allergy': ['sneezing', 'itchy eyes', 'watery eyes', 'runny nose', 'itchy throat']
        }

        key_list = key_symptoms.get(condition, [])
        return any(key in symptom for key in key_list)

    def determine_severity(self, condition_key):
        """Determine severity level"""
        severity_map = {
            'flu': 'MODERATE',
            'cold': 'MILD',
            'covid-19': 'MODERATE',
            'allergy': 'MILD'
        }
        return severity_map.get(condition_key, 'MODERATE')

    def save_knowledge_base_files(self, knowledge_base, output_dir):
        """Save knowledge base files"""
        try:
            # Main knowledge base
            with open(output_dir / 'medical_knowledge_base.json', 'w', encoding='utf-8') as f:
                json.dump(knowledge_base, f, indent=2, ensure_ascii=False)

            # Probability matrix
            with open(output_dir / 'probability_matrix.json', 'w', encoding='utf-8') as f:
                json.dump(knowledge_base['probability_matrix'], f, indent=2)

            # Symptoms index
            with open(output_dir / 'symptoms_index.json', 'w', encoding='utf-8') as f:
                json.dump(knowledge_base['symptoms_index'], f, indent=2)

            self.stdout.write('Knowledge base files updated with scraped data')

        except Exception as e:
            self.stdout.write(f'Error saving files: {e}')