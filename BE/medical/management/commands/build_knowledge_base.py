# BE/chatbot/management/commands/build_knowledge_base.py
import requests
import json
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from chatbot.models import MedicalCondition, Symptom, ConditionSymptom, SpecialistRecommendation
import time
import logging

logger = logging.getLogger(__name__)

class MedicalDataScraper:
    """
    Scrapes and processes medical data from various sources
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_mayo_clinic_condition(self, condition_url):
        """
        Scrape condition info from Mayo Clinic
        """
        try:
            response = self.session.get(condition_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract condition name
            name = soup.find('h1').get_text().strip()

            # Extract description/overview
            overview_section = soup.find('div', {'class': 'content'})
            description = ""
            if overview_section:
                paragraphs = overview_section.find_all('p')[:3]  # First 3 paragraphs
                description = ' '.join([p.get_text().strip() for p in paragraphs])

            # Extract symptoms
            symptoms = []
            symptoms_section = soup.find('section', id='symptoms')
            if symptoms_section:
                symptom_items = symptoms_section.find_all('li')
                symptoms = [item.get_text().strip() for item in symptom_items[:10]]

            # Extract when to see doctor (severity)
            severity = 'MODERATE'  # Default
            when_to_see = soup.find(text=lambda text: text and 'emergency' in text.lower())
            if when_to_see:
                severity = 'SEVERE'

            return {
                'name': name,
                'description': description,
                'severity_level': severity,
                'symptoms': symptoms,
                'source_url': condition_url
            }

        except Exception as e:
            logger.error(f"Error scraping {condition_url}: {e}")
            return None

    def scrape_webmd_condition(self, condition_name):
        """
        Scrape from WebMD (similar structure)
        """
        search_url = f"https://www.webmd.com/search/search_results/default.aspx?query={condition_name}"
        # Implementation similar to Mayo Clinic...
        pass

    def process_raw_data_to_model(self, raw_data):
        """
        Convert scraped data to fit our Django models.py
        """
        try:
            # Create or update MedicalCondition
            condition, created = MedicalCondition.objects.get_or_create(
                name=raw_data['name'],
                defaults={
                    'description': raw_data['description'],
                    'severity_level': raw_data['severity_level'],
                    'recommended_action': f"Consult a healthcare provider about {raw_data['name']}",
                    'source_websites': [raw_data['source_url']]
                }
            )

            # Process symptoms
            for symptom_text in raw_data['symptoms']:
                # Clean and normalize symptom text
                clean_symptom = self.normalize_symptom_text(symptom_text)

                # Create or get symptom
                symptom, created = Symptom.objects.get_or_create(
                    name=clean_symptom,
                    defaults={
                        'description': f"Symptom associated with {raw_data['name']}",
                        'is_common': len(clean_symptom.split()) <= 2  # Simple heuristic
                    }
                )

                # Create relationship with probability (you'll need to fine-tune this)
                probability = self.calculate_symptom_probability(symptom_text, raw_data['name'])
                is_primary = self.is_primary_symptom(symptom_text, raw_data['symptoms'])

                ConditionSymptom.objects.get_or_create(
                    condition=condition,
                    symptom=symptom,
                    defaults={
                        'probability': probability,
                        'is_primary': is_primary
                    }
                )

            # Create specialist recommendations
            specialist = self.recommend_specialist(raw_data['name'])
            urgency = self.determine_urgency(raw_data['severity_level'])

            SpecialistRecommendation.objects.get_or_create(
                condition=condition,
                specialist_type=specialist,
                defaults={
                    'urgency_level': urgency,
                    'notes': f"Recommended for {raw_data['name']} treatment"
                }
            )

            return condition

        except Exception as e:
            logger.error(f"Error processing data for {raw_data['name']}: {e}")
            return None

    def normalize_symptom_text(self, symptom_text):
        """
        Clean and normalize symptom descriptions
        """
        # Remove extra whitespace, convert to lowercase
        clean = ' '.join(symptom_text.strip().lower().split())

        # Remove common prefixes/suffixes
        prefixes_to_remove = ['severe', 'mild', 'chronic', 'acute']
        for prefix in prefixes_to_remove:
            if clean.startswith(prefix + ' '):
                clean = clean[len(prefix + ' '):]

        return clean.title()

    def calculate_symptom_probability(self, symptom_text, condition_name):
        """
        Calculate probability based on symptom importance
        (This is simplified - you'd want more sophisticated NLP)
        """
        # Keywords that indicate high probability
        high_prob_keywords = ['main', 'primary', 'common', 'typical', 'characteristic']
        low_prob_keywords = ['rare', 'occasional', 'sometimes', 'may', 'possible']

        symptom_lower = symptom_text.lower()

        if any(keyword in symptom_lower for keyword in high_prob_keywords):
            return 0.8
        elif any(keyword in symptom_lower for keyword in low_prob_keywords):
            return 0.3
        else:
            return 0.6  # Default moderate probability

    def is_primary_symptom(self, symptom_text, all_symptoms):
        """
        Determine if this is a primary symptom (appears early in list)
        """
        return all_symptoms.index(symptom_text) < 3  # First 3 are primary

    def recommend_specialist(self, condition_name):
        """
        Map conditions to specialists
        """
        specialist_mapping = {
            'flu': 'General Practitioner',
            'cold': 'General Practitioner',
            'covid': 'General Practitioner',
            'allergy': 'Allergist',
            'asthma': 'Pulmonologist',
            'diabetes': 'Endocrinologist',
            'hypertension': 'Cardiologist',
            'depression': 'Psychiatrist',
            'anxiety': 'Psychiatrist'
        }

        condition_lower = condition_name.lower()
        for key, specialist in specialist_mapping.items():
            if key in condition_lower:
                return specialist

        return 'General Practitioner'  # Default

    def determine_urgency(self, severity_level):
        """
        Map severity to urgency
        """
        mapping = {
            'MILD': 'LOW',
            'MODERATE': 'MEDIUM',
            'SEVERE': 'HIGH'
        }
        return mapping.get(severity_level, 'MEDIUM')


class Command(BaseCommand):
    help = 'Build medical knowledge base from web sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--conditions',
            nargs='+',
            type=str,
            help='List of conditions to scrape',
            default=['flu', 'cold', 'covid-19', 'allergies', 'asthma', 'diabetes']
        )

        parser.add_argument(
            '--source',
            type=str,
            choices=['mayo', 'webmd', 'all'],
            default='mayo',
            help='Which source to scrape from'
        )

        parser.add_argument(
            '--batch-size',
            type=int,
            default=5,
            help='Number of conditions to process in each batch'
        )

    def handle(self, *args, **options):
        scraper = MedicalDataScraper()
        conditions = options['conditions']
        source = options['source']
        batch_size = options['batch_size']

        self.stdout.write(f"Building knowledge base for {len(conditions)} conditions...")

        # Mayo Clinic condition URLs (you'd build this list)
        mayo_urls = {
            'flu': 'https://www.mayoclinic.org/diseases-conditions/flu/symptoms-causes/syc-20351719',
            'cold': 'https://www.mayoclinic.org/diseases-conditions/common-cold/symptoms-causes/syc-20351605',
            # Add more URLs...
        }

        processed = 0
        for i, condition in enumerate(conditions):
            if condition in mayo_urls:
                self.stdout.write(f"Processing {condition}...")

                # Scrape raw data
                raw_data = scraper.scrape_mayo_clinic_condition(mayo_urls[condition])

                if raw_data:
                    # Process and save to database
                    result = scraper.process_raw_data_to_model(raw_data)

                    if result:
                        processed += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Successfully processed {condition}")
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"✗ Failed to process {condition}")
                        )

                # Rate limiting - be respectful to websites
                time.sleep(2)

                # Batch processing
                if (i + 1) % batch_size == 0:
                    self.stdout.write(f"Processed batch {(i + 1) // batch_size}")
                    time.sleep(5)  # Longer pause between batches

        self.stdout.write(
            self.style.SUCCESS(f"Knowledge base building complete! Processed {processed}/{len(conditions)} conditions")
        )