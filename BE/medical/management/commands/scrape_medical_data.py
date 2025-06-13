# BE/medical/management/commands/scrape_medical_data.py
import requests
import time
import json
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from pathlib import Path
from ...models import MedicalCondition, Symptom, ConditionSymptom, SpecialistRecommendation
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape medical data from trusted websites'

    def add_arguments(self, parser):
        parser.add_argument(
            '--conditions',
            nargs='+',
            type=str,
            help='Conditions to scrape',
            default=['flu', 'cold', 'covid-19', 'allergy']
        )
        parser.add_argument(
            '--delay',
            type=int,
            default=3,
            help='Delay between requests in seconds'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting medical data scraping...')

        # Trusted medical websites
        self.medical_sources = {
            'mayo_clinic': 'https://www.mayoclinic.org',
            'webmd': 'https://www.webmd.com',
            'cdc': 'https://www.cdc.gov',
            'nhs': 'https://www.nhs.uk',
            'medlineplus': 'https://medlineplus.gov'
        }

        # URL patterns for each condition
        self.condition_urls = {
            'flu': [
                'https://www.mayoclinic.org/diseases-conditions/flu/symptoms-causes/syc-20351719',
                'https://www.webmd.com/cold-and-flu/flu-guide/what-is-flu',
                'https://www.cdc.gov/flu/symptoms/index.html',
                'https://www.nhs.uk/conditions/flu/',
                'https://medlineplus.gov/flu.html'
            ],
            'cold': [
                'https://www.mayoclinic.org/diseases-conditions/common-cold/symptoms-causes/syc-20351605',
                'https://www.webmd.com/cold-and-flu/cold-guide/common_cold',
                'https://www.cdc.gov/features/rhinoviruses/index.html',
                'https://www.nhs.uk/conditions/common-cold/',
                'https://medlineplus.gov/commoncold.html'
            ],
            'covid-19': [
                'https://www.mayoclinic.org/diseases-conditions/coronavirus/symptoms-causes/syc-20479963',
                'https://www.webmd.com/lung/coronavirus',
                'https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html',
                'https://www.nhs.uk/conditions/coronavirus-covid-19/',
                'https://medlineplus.gov/covid19coronavirusdisease2019.html'
            ],
            'allergy': [
                'https://www.mayoclinic.org/diseases-conditions/allergies/symptoms-causes/syc-20351497',
                'https://www.webmd.com/allergies/default.htm',
                'https://www.cdc.gov/nceh/airpollution/allergens/',
                'https://www.nhs.uk/conditions/allergies/',
                'https://medlineplus.gov/allergy.html'
            ]
        }

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        conditions = options['conditions']
        delay = options['delay']

        scraped_data = {}

        for condition in conditions:
            self.stdout.write(f'Scraping data for: {condition}')
            condition_data = self.scrape_condition(condition, delay)
            if condition_data:
                scraped_data[condition] = condition_data
                self.stdout.write(f'✓ Successfully scraped {condition}')
            else:
                self.stdout.write(f'✗ Failed to scrape {condition}')

        # Save scraped data
        self.save_scraped_data(scraped_data)

        # Update database
        self.update_database(scraped_data)

        self.stdout.write(self.style.SUCCESS('Medical data scraping completed!'))

    def scrape_condition(self, condition, delay):
        """Scrape data for a specific condition"""
        urls = self.condition_urls.get(condition, [])
        condition_data = {
            'name': condition.replace('-', ' ').title(),
            'symptoms': set(),
            'descriptions': [],
            'treatments': [],
            'sources': []
        }

        for url in urls:
            try:
                self.stdout.write(f'  Scraping: {url}')

                response = self.session.get(url, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract data based on website
                if 'mayoclinic.org' in url:
                    data = self.scrape_mayo_clinic(soup)
                elif 'webmd.com' in url:
                    data = self.scrape_webmd(soup)
                elif 'cdc.gov' in url:
                    data = self.scrape_cdc(soup)
                elif 'nhs.uk' in url:
                    data = self.scrape_nhs(soup)
                elif 'medlineplus.gov' in url:
                    data = self.scrape_medlineplus(soup)
                else:
                    data = self.scrape_generic(soup)

                if data:
                    condition_data['symptoms'].update(data.get('symptoms', []))
                    condition_data['descriptions'].extend(data.get('descriptions', []))
                    condition_data['treatments'].extend(data.get('treatments', []))
                    condition_data['sources'].append(url)

                time.sleep(delay)  # Rate limiting

            except Exception as e:
                self.stdout.write(f'    Error scraping {url}: {e}')
                continue

        # Convert set to list
        condition_data['symptoms'] = list(condition_data['symptoms'])

        return condition_data if condition_data['symptoms'] else None

    def scrape_mayo_clinic(self, soup):
        """Scrape Mayo Clinic pages"""
        data = {'symptoms': [], 'descriptions': [], 'treatments': []}

        try:
            # Extract symptoms
            symptoms_section = soup.find('div', {'class': 'content'}) or soup.find('main')
            if symptoms_section:
                # Look for symptom lists
                symptom_lists = symptoms_section.find_all(['ul', 'ol'])
                for ul in symptom_lists:
                    items = ul.find_all('li')
                    for item in items:
                        text = item.get_text().strip()
                        if text and len(text) < 100:  # Reasonable symptom length
                            data['symptoms'].append(text)

            # Extract descriptions
            paragraphs = soup.find_all('p')
            for p in paragraphs[:5]:  # First 5 paragraphs
                text = p.get_text().strip()
                if text and len(text) > 50:
                    data['descriptions'].append(text)

        except Exception as e:
            logger.error(f'Error scraping Mayo Clinic: {e}')

        return data

    def scrape_webmd(self, soup):
        """Scrape WebMD pages"""
        data = {'symptoms': [], 'descriptions': [], 'treatments': []}

        try:
            # Extract symptoms from lists
            symptom_lists = soup.find_all(['ul', 'ol'])
            for ul in symptom_lists:
                items = ul.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    if text and len(text) < 100:
                        data['symptoms'].append(text)

            # Extract descriptions
            paragraphs = soup.find_all('p')
            for p in paragraphs[:3]:
                text = p.get_text().strip()
                if text and len(text) > 50:
                    data['descriptions'].append(text)

        except Exception as e:
            logger.error(f'Error scraping WebMD: {e}')

        return data

    def scrape_cdc(self, soup):
        """Scrape CDC pages"""
        data = {'symptoms': [], 'descriptions': [], 'treatments': []}

        try:
            # CDC often uses specific classes
            content_divs = soup.find_all('div', {'class': ['content', 'page-content', 'syndicate']})
            for div in content_divs:
                # Look for symptom lists
                lists = div.find_all(['ul', 'ol'])
                for ul in lists:
                    items = ul.find_all('li')
                    for item in items:
                        text = item.get_text().strip()
                        if text and len(text) < 100:
                            data['symptoms'].append(text)

            # Extract descriptions
            paragraphs = soup.find_all('p')
            for p in paragraphs[:3]:
                text = p.get_text().strip()
                if text and len(text) > 50:
                    data['descriptions'].append(text)

        except Exception as e:
            logger.error(f'Error scraping CDC: {e}')

        return data

    def scrape_nhs(self, soup):
        """Scrape NHS pages"""
        data = {'symptoms': [], 'descriptions': [], 'treatments': []}

        try:
            # NHS uses specific structure
            main_content = soup.find('main') or soup.find('div', {'class': 'nhsuk-main-wrapper'})
            if main_content:
                lists = main_content.find_all(['ul', 'ol'])
                for ul in lists:
                    items = ul.find_all('li')
                    for item in items:
                        text = item.get_text().strip()
                        if text and len(text) < 100:
                            data['symptoms'].append(text)

            # Extract descriptions
            paragraphs = soup.find_all('p')
            for p in paragraphs[:3]:
                text = p.get_text().strip()
                if text and len(text) > 50:
                    data['descriptions'].append(text)

        except Exception as e:
            logger.error(f'Error scraping NHS: {e}')

        return data

    def scrape_medlineplus(self, soup):
        """Scrape MedlinePlus pages"""
        data = {'symptoms': [], 'descriptions': [], 'treatments': []}

        try:
            # MedlinePlus structure
            content = soup.find('div', {'id': 'mplus-content'}) or soup.find('main')
            if content:
                lists = content.find_all(['ul', 'ol'])
                for ul in lists:
                    items = ul.find_all('li')
                    for item in items:
                        text = item.get_text().strip()
                        if text and len(text) < 100:
                            data['symptoms'].append(text)

            # Extract descriptions
            paragraphs = soup.find_all('p')
            for p in paragraphs[:3]:
                text = p.get_text().strip()
                if text and len(text) > 50:
                    data['descriptions'].append(text)

        except Exception as e:
            logger.error(f'Error scraping MedlinePlus: {e}')

        return data

    def scrape_generic(self, soup):
        """Generic scraping for unknown websites"""
        data = {'symptoms': [], 'descriptions': [], 'treatments': []}

        try:
            # Generic approach - look for lists and paragraphs
            lists = soup.find_all(['ul', 'ol'])
            for ul in lists:
                items = ul.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    if text and len(text) < 100:
                        data['symptoms'].append(text)

            paragraphs = soup.find_all('p')
            for p in paragraphs[:3]:
                text = p.get_text().strip()
                if text and len(text) > 50:
                    data['descriptions'].append(text)

        except Exception as e:
            logger.error(f'Error in generic scraping: {e}')

        return data

    def save_scraped_data(self, scraped_data):
        """Save scraped data to JSON file"""
        try:
            output_dir = Path('medical_knowledge')
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save with timestamp
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f'scraped_medical_data_{timestamp}.json'

            with open(output_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, indent=2, ensure_ascii=False)

            self.stdout.write(f'Scraped data saved to: {filename}')

        except Exception as e:
            self.stdout.write(f'Error saving scraped data: {e}')

    def update_database(self, scraped_data):
        """Update database with scraped data"""
        try:
            for condition_key, condition_data in scraped_data.items():
                self.stdout.write(f'Updating database for: {condition_key}')

                # Update or create condition
                condition, created = MedicalCondition.objects.update_or_create(
                    name=condition_data['name'],
                    defaults={
                        'description': ' '.join(condition_data['descriptions'][:2]),  # First 2 descriptions
                        'severity_level': self.determine_severity(condition_key),
                        'recommended_action': ' '.join(condition_data['treatments'][:1]) if condition_data['treatments'] else 'Consult healthcare provider',
                        'source_websites': condition_data['sources']
                    }
                )

                # Process symptoms
                for symptom_text in condition_data['symptoms']:
                    if symptom_text and len(symptom_text.strip()) > 2:
                        # Clean symptom text
                        clean_symptom = self.clean_symptom_text(symptom_text)

                        if clean_symptom:
                            # Create or get symptom
                            symptom, created = Symptom.objects.get_or_create(
                                name=clean_symptom,
                                defaults={
                                    'description': f'Symptom associated with {condition_data["name"]}',
                                    'is_common': self.is_common_symptom(clean_symptom)
                                }
                            )

                            # Create relationship
                            ConditionSymptom.objects.get_or_create(
                                condition=condition,
                                symptom=symptom,
                                defaults={
                                    'probability': self.calculate_probability(clean_symptom, condition_key),
                                    'is_primary': self.is_primary_symptom(clean_symptom, condition_key)
                                }
                            )

                # Create specialist recommendation
                specialist, urgency = self.get_specialist_recommendation(condition_key)
                SpecialistRecommendation.objects.get_or_create(
                    condition=condition,
                    specialist_type=specialist,
                    defaults={
                        'urgency_level': urgency,
                        'notes': f'Recommended specialist for {condition_data["name"]} based on web sources'
                    }
                )

                self.stdout.write(f'✓ Updated {condition_key} with {len(condition_data["symptoms"])} symptoms')

        except Exception as e:
            self.stdout.write(f'Error updating database: {e}')

    def clean_symptom_text(self, symptom_text):
        """Clean and normalize symptom text"""
        # Remove extra whitespace and convert to title case
        clean = ' '.join(symptom_text.strip().split())

        # Remove common prefixes
        prefixes = ['Symptoms include', 'May include', 'Common symptoms:', 'You may have']
        for prefix in prefixes:
            if clean.startswith(prefix):
                clean = clean[len(prefix):].strip()

        # Remove trailing punctuation
        clean = clean.rstrip('.,;:')

        return clean.title() if clean else None

    def determine_severity(self, condition_key):
        """Determine severity level based on condition"""
        severity_map = {
            'flu': 'MODERATE',
            'cold': 'MILD',
            'covid-19': 'MODERATE',
            'allergy': 'MILD'
        }
        return severity_map.get(condition_key, 'MODERATE')

    def is_common_symptom(self, symptom):
        """Determine if symptom is common"""
        common_symptoms = ['fever', 'cough', 'fatigue', 'headache', 'runny nose', 'sore throat', 'sneezing']
        return any(common in symptom.lower() for common in common_symptoms)

    def calculate_probability(self, symptom, condition):
        """Calculate symptom probability based on condition"""
        # High probability symptoms
        high_prob_symptoms = {
            'flu': ['fever', 'body aches', 'fatigue', 'chills'],
            'cold': ['runny nose', 'sneezing', 'sore throat'],
            'covid-19': ['loss of taste', 'loss of smell', 'cough'],
            'allergy': ['sneezing', 'itchy eyes', 'watery eyes']
        }

        symptom_lower = symptom.lower()
        high_symptoms = high_prob_symptoms.get(condition, [])

        if any(high_symptom in symptom_lower for high_symptom in high_symptoms):
            return 0.8
        else:
            return 0.6

    def is_primary_symptom(self, symptom, condition):
        """Determine if symptom is primary for condition"""
        primary_symptoms = {
            'flu': ['fever', 'body aches', 'fatigue'],
            'cold': ['runny nose', 'sneezing'],
            'covid-19': ['loss of taste', 'loss of smell'],
            'allergy': ['sneezing', 'itchy eyes']
        }

        symptom_lower = symptom.lower()
        primary = primary_symptoms.get(condition, [])

        return any(primary_symptom in symptom_lower for primary_symptom in primary)

    def get_specialist_recommendation(self, condition):
        """Get specialist recommendation for condition"""
        recommendations = {
            'flu': ('General Practitioner', 'MEDIUM'),
            'cold': ('General Practitioner', 'LOW'),
            'covid-19': ('General Practitioner', 'HIGH'),
            'allergy': ('Allergist', 'LOW')
        }
        return recommendations.get(condition, ('General Practitioner', 'MEDIUM'))