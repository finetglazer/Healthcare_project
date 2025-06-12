# BE/medical/management/commands/build_comprehensive_knowledge_base.py
import requests
import json
import time
import logging
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from ...models import MedicalCondition, Symptom, ConditionSymptom, SpecialistRecommendation
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class MedicalDataCollector:
    """
    Comprehensive medical data collector from multiple reputable sources
    """

    def __init__(self, output_dir="E:/PTTK/medical_knowledge"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Reputable medical sources
        self.medical_sources = {
            'mayo_clinic': {
                'base_url': 'https://www.mayoclinic.org',
                'conditions': {
                    'flu': '/diseases-conditions/flu/symptoms-causes/syc-20351719',
                    'cold': '/diseases-conditions/common-cold/symptoms-causes/syc-20351605',
                    'covid-19': '/diseases-conditions/coronavirus/symptoms-causes/syc-20479963',
                    'allergies': '/diseases-conditions/allergies/symptoms-causes/syc-20351497'
                }
            },
            'webmd': {
                'base_url': 'https://www.webmd.com',
                'conditions': {
                    'flu': '/cold-and-flu/flu-guide/flu-symptoms',
                    'cold': '/cold-and-flu/cold-guide/common_cold',
                    'covid-19': '/lung/coronavirus-symptoms',
                    'allergies': '/allergies/guide/allergy-symptoms'
                }
            },
            'healthline': {
                'base_url': 'https://www.healthline.com',
                'conditions': {
                    'flu': '/health/flu/symptoms',
                    'cold': '/health/common-cold-symptoms',
                    'covid-19': '/health/coronavirus-symptoms',
                    'allergies': '/health/allergies/symptoms'
                }
            },
            'medlineplus': {
                'base_url': 'https://medlineplus.gov',
                'conditions': {
                    'flu': '/influenza.html',
                    'cold': '/commoncold.html',
                    'covid-19': '/covid19coronavirusdisease2019.html',
                    'allergies': '/allergy.html'
                }
            },
            'who': {
                'base_url': 'https://www.who.int',
                'conditions': {
                    'covid-19': '/health-topics/coronavirus#tab=tab_3'
                }
            }
        }

        # Enhanced symptom patterns with severity and duration
        self.symptom_database = {
            'flu': {
                'primary_symptoms': [
                    {'name': 'High Fever', 'severity': ['moderate', 'severe'], 'duration': '3-7 days', 'probability': 0.9},
                    {'name': 'Body Aches', 'severity': ['moderate', 'severe'], 'duration': '3-5 days', 'probability': 0.9},
                    {'name': 'Fatigue', 'severity': ['moderate', 'severe'], 'duration': '7-14 days', 'probability': 0.8},
                    {'name': 'Chills', 'severity': ['moderate', 'severe'], 'duration': '1-3 days', 'probability': 0.8},
                    {'name': 'Headache', 'severity': ['moderate', 'severe'], 'duration': '2-5 days', 'probability': 0.7}
                ],
                'secondary_symptoms': [
                    {'name': 'Dry Cough', 'severity': ['mild', 'moderate'], 'duration': '7-10 days', 'probability': 0.6},
                    {'name': 'Sore Throat', 'severity': ['mild', 'moderate'], 'duration': '2-4 days', 'probability': 0.5},
                    {'name': 'Runny Nose', 'severity': ['mild'], 'duration': '3-7 days', 'probability': 0.4}
                ],
                'combinations': [
                    {'symptoms': ['High Fever', 'Body Aches', 'Fatigue'], 'probability': 0.95},
                    {'symptoms': ['Fever', 'Chills', 'Headache'], 'probability': 0.85}
                ]
            },
            'cold': {
                'primary_symptoms': [
                    {'name': 'Runny Nose', 'severity': ['mild', 'moderate'], 'duration': '7-10 days', 'probability': 0.9},
                    {'name': 'Sneezing', 'severity': ['mild', 'moderate'], 'duration': '3-7 days', 'probability': 0.8},
                    {'name': 'Sore Throat', 'severity': ['mild', 'moderate'], 'duration': '2-5 days', 'probability': 0.7},
                    {'name': 'Congestion', 'severity': ['mild', 'moderate'], 'duration': '5-10 days', 'probability': 0.8}
                ],
                'secondary_symptoms': [
                    {'name': 'Mild Cough', 'severity': ['mild'], 'duration': '7-14 days', 'probability': 0.6},
                    {'name': 'Low-grade Fever', 'severity': ['mild'], 'duration': '1-3 days', 'probability': 0.3},
                    {'name': 'Mild Fatigue', 'severity': ['mild'], 'duration': '3-7 days', 'probability': 0.4}
                ],
                'combinations': [
                    {'symptoms': ['Runny Nose', 'Sneezing', 'Sore Throat'], 'probability': 0.85},
                    {'symptoms': ['Congestion', 'Runny Nose'], 'probability': 0.8}
                ]
            },
            'covid-19': {
                'primary_symptoms': [
                    {'name': 'Loss of Taste', 'severity': ['moderate', 'severe'], 'duration': '7-30 days', 'probability': 0.8},
                    {'name': 'Loss of Smell', 'severity': ['moderate', 'severe'], 'duration': '7-30 days', 'probability': 0.8},
                    {'name': 'Persistent Cough', 'severity': ['moderate', 'severe'], 'duration': '14-21 days', 'probability': 0.7},
                    {'name': 'Fever', 'severity': ['moderate', 'severe'], 'duration': '3-10 days', 'probability': 0.7}
                ],
                'secondary_symptoms': [
                    {'name': 'Fatigue', 'severity': ['moderate', 'severe'], 'duration': '14-60 days', 'probability': 0.6},
                    {'name': 'Shortness of Breath', 'severity': ['moderate', 'severe'], 'duration': '7-30 days', 'probability': 0.5},
                    {'name': 'Sore Throat', 'severity': ['mild', 'moderate'], 'duration': '3-7 days', 'probability': 0.4},
                    {'name': 'Headache', 'severity': ['mild', 'moderate'], 'duration': '3-10 days', 'probability': 0.4}
                ],
                'combinations': [
                    {'symptoms': ['Loss of Taste', 'Loss of Smell'], 'probability': 0.9},
                    {'symptoms': ['Persistent Cough', 'Fever', 'Fatigue'], 'probability': 0.8},
                    {'symptoms': ['Loss of Taste', 'Persistent Cough'], 'probability': 0.75}
                ]
            },
            'allergy': {
                'primary_symptoms': [
                    {'name': 'Sneezing Fits', 'severity': ['mild', 'moderate'], 'duration': 'varies', 'probability': 0.9},
                    {'name': 'Itchy Eyes', 'severity': ['mild', 'moderate'], 'duration': 'varies', 'probability': 0.8},
                    {'name': 'Watery Eyes', 'severity': ['mild', 'moderate'], 'duration': 'varies', 'probability': 0.8},
                    {'name': 'Clear Runny Nose', 'severity': ['mild', 'moderate'], 'duration': 'varies', 'probability': 0.8}
                ],
                'secondary_symptoms': [
                    {'name': 'Itchy Throat', 'severity': ['mild'], 'duration': 'varies', 'probability': 0.6},
                    {'name': 'Skin Rash', 'severity': ['mild', 'moderate'], 'duration': 'varies', 'probability': 0.4},
                    {'name': 'Congestion', 'severity': ['mild', 'moderate'], 'duration': 'varies', 'probability': 0.5}
                ],
                'combinations': [
                    {'symptoms': ['Sneezing Fits', 'Itchy Eyes', 'Watery Eyes'], 'probability': 0.9},
                    {'symptoms': ['Clear Runny Nose', 'Sneezing Fits'], 'probability': 0.8}
                ]
            }
        }

    def scrape_mayo_clinic(self, condition, url):
        """Scrape Mayo Clinic for symptom information"""
        try:
            full_url = urljoin(self.medical_sources['mayo_clinic']['base_url'], url)
            response = self.session.get(full_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            symptoms = []

            # Look for symptoms section
            symptoms_section = soup.find('section', {'data-module': 'symptoms'}) or \
                               soup.find('div', class_=re.compile('symptoms', re.I))

            if symptoms_section:
                # Extract symptom list items
                symptom_items = symptoms_section.find_all(['li', 'p'])
                for item in symptom_items:
                    text = item.get_text().strip()
                    if text and len(text) > 10 and not text.lower().startswith('when to'):
                        symptoms.append(self.clean_symptom_text(text))

            return {
                'source': 'Mayo Clinic',
                'url': full_url,
                'condition': condition,
                'symptoms': symptoms[:15]  # Limit to top 15
            }

        except Exception as e:
            logger.error(f"Error scraping Mayo Clinic for {condition}: {e}")
            return None

    def scrape_webmd(self, condition, url):
        """Scrape WebMD for symptom information"""
        try:
            full_url = urljoin(self.medical_sources['webmd']['base_url'], url)
            response = self.session.get(full_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            symptoms = []

            # WebMD specific selectors
            symptom_containers = soup.find_all(['div', 'section'],
                                               class_=re.compile('symptom|sign', re.I))

            for container in symptom_containers:
                items = container.find_all(['li', 'p'])
                for item in items:
                    text = item.get_text().strip()
                    if text and len(text) > 5:
                        symptoms.append(self.clean_symptom_text(text))

            return {
                'source': 'WebMD',
                'url': full_url,
                'condition': condition,
                'symptoms': symptoms[:15]
            }

        except Exception as e:
            logger.error(f"Error scraping WebMD for {condition}: {e}")
            return None

    def clean_symptom_text(self, text):
        """Clean and normalize symptom text"""
        # Remove extra whitespace and common prefixes
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'^(Signs and symptoms include|Symptoms include|Common symptoms)', '', text, flags=re.I)
        text = re.sub(r'^(may include|include|such as):', '', text, flags=re.I)

        # Remove sentence endings for list items
        text = re.sub(r'[.;,]\s*$', '', text)

        return text.strip()

    def build_knowledge_base(self):
        """Build comprehensive knowledge base"""
        logger.info("Building comprehensive medical knowledge base...")

        # Create output structure
        knowledge_base = {
            'metadata': {
                'version': '1.0',
                'created': time.strftime('%Y-%m-%d %H:%M:%S'),
                'conditions_count': 4,
                'sources': list(self.medical_sources.keys())
            },
            'conditions': {},
            'symptoms_index': {},
            'probability_matrix': {},
            'differential_diagnosis': {}
        }

        # Process each condition
        for condition in ['flu', 'cold', 'covid-19', 'allergy']:
            logger.info(f"Processing {condition}...")

            condition_data = {
                'name': condition.replace('-', ' ').title(),
                'symptoms': self.symptom_database.get(condition, {}),
                'scraped_data': [],
                'specialist_recommendation': self.get_specialist_recommendation(condition)
            }

            # Scrape from multiple sources
            for source_name, source_config in self.medical_sources.items():
                if condition in source_config['conditions']:
                    logger.info(f"Scraping {source_name} for {condition}...")

                    if source_name == 'mayo_clinic':
                        scraped = self.scrape_mayo_clinic(condition, source_config['conditions'][condition])
                    elif source_name == 'webmd':
                        scraped = self.scrape_webmd(condition, source_config['conditions'][condition])
                    else:
                        # Generic scraping for other sources
                        scraped = self.generic_scrape(source_name, condition, source_config)

                    if scraped:
                        condition_data['scraped_data'].append(scraped)

                    # Rate limiting
                    time.sleep(2)

            knowledge_base['conditions'][condition] = condition_data

            # Build symptoms index
            self.build_symptoms_index(condition, condition_data, knowledge_base['symptoms_index'])

        # Build probability matrix
        knowledge_base['probability_matrix'] = self.build_probability_matrix()

        # Build differential diagnosis rules
        knowledge_base['differential_diagnosis'] = self.build_differential_diagnosis()

        # Save to files
        self.save_knowledge_base(knowledge_base)

        return knowledge_base

    def generic_scrape(self, source_name, condition, source_config):
        """Generic scraping method for other sources"""
        try:
            full_url = urljoin(source_config['base_url'], source_config['conditions'][condition])
            response = self.session.get(full_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Generic symptom extraction
            symptoms = []

            # Look for common symptom patterns
            for element in soup.find_all(['li', 'p']):
                text = element.get_text().strip()
                if self.is_symptom_text(text):
                    symptoms.append(self.clean_symptom_text(text))

            return {
                'source': source_name.replace('_', ' ').title(),
                'url': full_url,
                'condition': condition,
                'symptoms': symptoms[:10]
            }

        except Exception as e:
            logger.error(f"Error scraping {source_name} for {condition}: {e}")
            return None

    def is_symptom_text(self, text):
        """Check if text describes a symptom"""
        symptom_keywords = [
            'fever', 'cough', 'pain', 'ache', 'sore', 'runny', 'stuffy',
            'sneezing', 'fatigue', 'tired', 'headache', 'nausea', 'vomiting',
            'diarrhea', 'congestion', 'shortness', 'breath', 'difficulty',
            'loss', 'taste', 'smell', 'chills', 'sweats', 'rash', 'itchy'
        ]

        text_lower = text.lower()
        return (any(keyword in text_lower for keyword in symptom_keywords) and
                len(text) > 10 and len(text) < 200 and
                not text_lower.startswith(('when to', 'call', 'see', 'contact')))

    def build_symptoms_index(self, condition, condition_data, symptoms_index):
        """Build searchable symptoms index"""
        for symptom_category in ['primary_symptoms', 'secondary_symptoms']:
            if symptom_category in condition_data['symptoms']:
                for symptom in condition_data['symptoms'][symptom_category]:
                    symptom_name = symptom['name'].lower()

                    if symptom_name not in symptoms_index:
                        symptoms_index[symptom_name] = {
                            'conditions': {},
                            'aliases': [],
                            'category': 'primary' if 'primary' in symptom_category else 'secondary'
                        }

                    symptoms_index[symptom_name]['conditions'][condition] = {
                        'probability': symptom['probability'],
                        'severity': symptom['severity'],
                        'duration': symptom['duration']
                    }

    def build_probability_matrix(self):
        """Build probability matrix for AI processing"""
        matrix = {}

        for condition, data in self.symptom_database.items():
            matrix[condition] = {}

            # Primary symptoms
            for symptom in data.get('primary_symptoms', []):
                matrix[condition][symptom['name'].lower()] = {
                    'base_probability': symptom['probability'],
                    'is_primary': True,
                    'severity_modifier': {
                        'mild': 0.8,
                        'moderate': 1.0,
                        'severe': 1.2
                    }
                }

            # Secondary symptoms
            for symptom in data.get('secondary_symptoms', []):
                matrix[condition][symptom['name'].lower()] = {
                    'base_probability': symptom['probability'],
                    'is_primary': False,
                    'severity_modifier': {
                        'mild': 0.9,
                        'moderate': 1.0,
                        'severe': 1.1
                    }
                }

        return matrix

    def build_differential_diagnosis(self):
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
                    'allergy_indicators': ['itchy eyes', 'sneezing fits', 'clear discharge'],
                    'cold_indicators': ['sore throat', 'progression of symptoms', 'thick discharge'],
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

    def get_specialist_recommendation(self, condition):
        """Get specialist recommendations for each condition"""
        recommendations = {
            'flu': {
                'specialist': 'General Practitioner',
                'urgency': 'MEDIUM',
                'notes': 'Rest, hydration, antiviral medication if severe'
            },
            'cold': {
                'specialist': 'General Practitioner',
                'urgency': 'LOW',
                'notes': 'Rest, hydration, symptom management'
            },
            'covid-19': {
                'specialist': 'General Practitioner',
                'urgency': 'HIGH',
                'notes': 'Isolation, testing, monitoring for complications'
            },
            'allergy': {
                'specialist': 'Allergist',
                'urgency': 'LOW',
                'notes': 'Identify triggers, antihistamines, allergy testing'
            }
        }
        return recommendations.get(condition, {})

    def save_knowledge_base(self, knowledge_base):
        """Save knowledge base to multiple formats"""

        # Save main JSON file
        json_file = self.output_dir / 'medical_knowledge_base.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)

        # Save probability matrix for AI
        matrix_file = self.output_dir / 'probability_matrix.json'
        with open(matrix_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base['probability_matrix'], f, indent=2)

        # Save symptoms index
        symptoms_file = self.output_dir / 'symptoms_index.json'
        with open(symptoms_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base['symptoms_index'], f, indent=2)

        # Save differential diagnosis rules
        diff_file = self.output_dir / 'differential_diagnosis.json'
        with open(diff_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base['differential_diagnosis'], f, indent=2)

        logger.info(f"Knowledge base saved to {self.output_dir}")

    def populate_django_database(self, knowledge_base):
        """Populate Django database with collected data"""
        logger.info("Populating Django database...")

        for condition_name, condition_data in knowledge_base['conditions'].items():
            # Create or update condition
            condition, created = MedicalCondition.objects.get_or_create(
                name=condition_data['name'],
                defaults={
                    'description': f"Comprehensive data for {condition_data['name']}",
                    'severity_level': 'MODERATE',  # Default
                    'recommended_action': condition_data.get('specialist_recommendation', {}).get('notes', ''),
                    'source_websites': [item['url'] for item in condition_data.get('scraped_data', [])]
                }
            )

            # Process symptoms
            for category in ['primary_symptoms', 'secondary_symptoms']:
                if category in condition_data['symptoms']:
                    for symptom_data in condition_data['symptoms'][category]:
                        # Create or get symptom
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
            specialist_data = condition_data.get('specialist_recommendation', {})
            if specialist_data:
                SpecialistRecommendation.objects.get_or_create(
                    condition=condition,
                    specialist_type=specialist_data.get('specialist', 'General Practitioner'),
                    defaults={
                        'urgency_level': specialist_data.get('urgency', 'MEDIUM'),
                        'notes': specialist_data.get('notes', '')
                    }
                )

        logger.info("Django database populated successfully!")


class Command(BaseCommand):
    help = 'Build comprehensive medical knowledge base for chatbot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='E:/PTTK/medical_knowledge',
            help='Output directory for knowledge base files'
        )

        parser.add_argument(
            '--skip-scraping',
            action='store_true',
            help='Skip web scraping, use only structured data'
        )

        parser.add_argument(
            '--populate-db',
            action='store_true',
            help='Populate Django database with collected data'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        skip_scraping = options['skip_scraping']
        populate_db = options['populate_db']

        self.stdout.write('Building comprehensive medical knowledge base...')

        collector = MedicalDataCollector(output_dir)

        if skip_scraping:
            # Use only structured data
            knowledge_base = {
                'conditions': {},
                'symptoms_index': {},
                'probability_matrix': collector.build_probability_matrix(),
                'differential_diagnosis': collector.build_differential_diagnosis()
            }

            for condition in ['flu', 'cold', 'covid-19', 'allergy']:
                knowledge_base['conditions'][condition] = {
                    'name': condition.replace('-', ' ').title(),
                    'symptoms': collector.symptom_database.get(condition, {}),
                    'specialist_recommendation': collector.get_specialist_recommendation(condition)
                }
        else:
            # Full scraping and processing
            knowledge_base = collector.build_knowledge_base()

        if populate_db:
            collector.populate_django_database(knowledge_base)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully built knowledge base! '
                f'Files saved to: {output_dir}'
            )
        )