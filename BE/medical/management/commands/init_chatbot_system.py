# BE/medical/management/commands/init_chatbot_system.py
import json
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.cache import cache
from ...services.enhanced_analyzer import EnhancedSymptomAnalyzer
from ...services.chatbot_engine import ChatbotEngine
from ...models.condition import MedicalCondition
from ...models.sympton import Symptom, ConditionSymptom
from ...models.recommendation import SpecialistRecommendation

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize and test the chatbot system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-analysis',
            action='store_true',
            help='Run test analysis with sample symptoms'
        )
        parser.add_argument(
            '--rebuild-knowledge',
            action='store_true',
            help='Rebuild knowledge base from database'
        )
        parser.add_argument(
            '--create-sample-data',
            action='store_true',
            help='Create sample medical data for testing'
        )
        parser.add_argument(
            '--validate-system',
            action='store_true',
            help='Validate all system components'
        )

    def handle(self, *args, **options):
        self.stdout.write('🏥 Initializing Chatbot System...')

        try:
            # Validate system components
            if options['validate_system']:
                self.validate_system_components()

            # Create sample data if requested
            if options['create_sample_data']:
                self.create_sample_medical_data()

            # Rebuild knowledge base if requested  
            if options['rebuild_knowledge']:
                self.rebuild_knowledge_base()

            # Initialize system components
            self.initialize_components()

            # Run test analysis if requested
            if options['test_analysis']:
                self.run_test_analysis()

            self.stdout.write(
                self.style.SUCCESS('✅ Chatbot system initialized successfully!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Initialization failed: {e}')
            )

    def validate_system_components(self):
        """Validate all system components are working"""
        self.stdout.write('🔍 Validating system components...')

        # Test knowledge base directory
        kb_dir = Path(settings.BASE_DIR) / "medical_knowledge"
        if not kb_dir.exists():
            self.stdout.write('⚠️  Knowledge base directory not found, will be created')
            kb_dir.mkdir(parents=True, exist_ok=True)

        # Test database models
        try:
            condition_count = MedicalCondition.objects.count()
            symptom_count = Symptom.objects.count()
            self.stdout.write(f'📊 Database: {condition_count} conditions, {symptom_count} symptoms')
        except Exception as e:
            self.stdout.write(f'⚠️  Database issue: {e}')

        # Test cache system
        try:
            cache.set('test_key', 'test_value', 10)
            if cache.get('test_key') == 'test_value':
                self.stdout.write('✅ Cache system working')
            else:
                self.stdout.write('⚠️  Cache system not working')
        except Exception as e:
            self.stdout.write(f'⚠️  Cache error: {e}')

        # Test analyzer initialization
        try:
            analyzer = EnhancedSymptomAnalyzer()
            if analyzer.knowledge_base:
                conditions_count = len(analyzer.knowledge_base.get('conditions', {}))
                self.stdout.write(f'✅ Analyzer: {conditions_count} conditions loaded')
            else:
                self.stdout.write('⚠️  Analyzer: No knowledge base loaded')
        except Exception as e:
            self.stdout.write(f'⚠️  Analyzer error: {e}')

        # Test chatbot engine
        try:
            engine = ChatbotEngine()
            self.stdout.write('✅ Chatbot engine initialized')
        except Exception as e:
            self.stdout.write(f'⚠️  Chatbot engine error: {e}')

    def create_sample_medical_data(self):
        """Create sample medical data for testing"""
        self.stdout.write('📝 Creating sample medical data...')

        # Sample conditions data
        sample_conditions = [
            {
                'name': 'Influenza (Flu)',
                'description': 'Viral respiratory illness caused by influenza viruses',
                'severity_level': 'MODERATE',
                'symptoms': [
                    {'name': 'High Fever', 'probability': 0.9, 'is_primary': True},
                    {'name': 'Body Aches', 'probability': 0.8, 'is_primary': True},
                    {'name': 'Fatigue', 'probability': 0.8, 'is_primary': True},
                    {'name': 'Chills', 'probability': 0.7, 'is_primary': False},
                    {'name': 'Headache', 'probability': 0.6, 'is_primary': False},
                    {'name': 'Dry Cough', 'probability': 0.5, 'is_primary': False}
                ]
            },
            {
                'name': 'Common Cold',
                'description': 'Viral upper respiratory tract infection',
                'severity_level': 'MILD',
                'symptoms': [
                    {'name': 'Runny Nose', 'probability': 0.9, 'is_primary': True},
                    {'name': 'Sneezing', 'probability': 0.8, 'is_primary': True},
                    {'name': 'Sore Throat', 'probability': 0.7, 'is_primary': True},
                    {'name': 'Congestion', 'probability': 0.8, 'is_primary': False},
                    {'name': 'Mild Cough', 'probability': 0.6, 'is_primary': False},
                    {'name': 'Low Grade Fever', 'probability': 0.3, 'is_primary': False}
                ]
            },
            {
                'name': 'COVID-19',
                'description': 'Coronavirus disease caused by SARS-CoV-2',
                'severity_level': 'MODERATE',
                'symptoms': [
                    {'name': 'Fever', 'probability': 0.7, 'is_primary': True},
                    {'name': 'Dry Cough', 'probability': 0.8, 'is_primary': True},
                    {'name': 'Loss of Taste', 'probability': 0.6, 'is_primary': True},
                    {'name': 'Loss of Smell', 'probability': 0.6, 'is_primary': True},
                    {'name': 'Fatigue', 'probability': 0.7, 'is_primary': False},
                    {'name': 'Shortness of Breath', 'probability': 0.4, 'is_primary': False}
                ]
            },
            {
                'name': 'Allergic Reaction',
                'description': 'Immune system response to allergens',
                'severity_level': 'MILD',
                'symptoms': [
                    {'name': 'Sneezing', 'probability': 0.9, 'is_primary': True},
                    {'name': 'Itchy Eyes', 'probability': 0.8, 'is_primary': True},
                    {'name': 'Watery Eyes', 'probability': 0.7, 'is_primary': True},
                    {'name': 'Runny Nose', 'probability': 0.8, 'is_primary': False},
                    {'name': 'Skin Rash', 'probability': 0.5, 'is_primary': False},
                    {'name': 'Itchy Throat', 'probability': 0.6, 'is_primary': False}
                ]
            }
        ]

        # Create conditions and symptoms
        for condition_data in sample_conditions:
            # Create or update condition
            condition, created = MedicalCondition.objects.update_or_create(
                name=condition_data['name'],
                defaults={
                    'description': condition_data['description'],
                    'severity_level': condition_data['severity_level'],
                    'recommended_action': f"Consult healthcare provider about {condition_data['name']}"
                }
            )

            if created:
                self.stdout.write(f'  ✅ Created condition: {condition.name}')

            # Create symptoms and relationships
            for symptom_data in condition_data['symptoms']:
                symptom, created = Symptom.objects.update_or_create(
                    name=symptom_data['name'],
                    defaults={
                        'description': f"Symptom: {symptom_data['name']}",
                        'is_common': symptom_data['probability'] > 0.7
                    }
                )

                # Create condition-symptom relationship
                relationship, created = ConditionSymptom.objects.update_or_create(
                    condition=condition,
                    symptom=symptom,
                    defaults={
                        'probability': symptom_data['probability'],
                        'is_primary': symptom_data['is_primary']
                    }
                )

        # Create specialist recommendations
        specialist_recommendations = [
            {'condition': 'Influenza (Flu)', 'specialist': 'General Practitioner', 'urgency': 'MEDIUM'},
            {'condition': 'Common Cold', 'specialist': 'General Practitioner', 'urgency': 'LOW'},
            {'condition': 'COVID-19', 'specialist': 'Infectious Disease Specialist', 'urgency': 'MEDIUM'},
            {'condition': 'Allergic Reaction', 'specialist': 'Allergist', 'urgency': 'LOW'}
        ]

        for rec_data in specialist_recommendations:
            try:
                condition = MedicalCondition.objects.get(name=rec_data['condition'])
                recommendation, created = SpecialistRecommendation.objects.update_or_create(
                    condition=condition,
                    specialist_type=rec_data['specialist'],
                    defaults={
                        'urgency_level': rec_data['urgency'],
                        'notes': f"Recommended specialist for {condition.name}"
                    }
                )
            except MedicalCondition.DoesNotExist:
                continue

        self.stdout.write('✅ Sample medical data created')

    def rebuild_knowledge_base(self):
        """Rebuild knowledge base from database"""
        self.stdout.write('🔄 Rebuilding knowledge base...')

        try:
            analyzer = EnhancedSymptomAnalyzer()
            analyzer.build_from_database()

            # Clear cache to force reload
            cache.delete('knowledge_base_data')

            self.stdout.write('✅ Knowledge base rebuilt from database')

        except Exception as e:
            self.stdout.write(f'❌ Knowledge base rebuild failed: {e}')

    def initialize_components(self):
        """Initialize all system components"""
        self.stdout.write('🚀 Initializing components...')

        # Initialize analyzer
        try:
            analyzer = EnhancedSymptomAnalyzer()
            conditions_count = len(analyzer.knowledge_base.get('conditions', {})) if analyzer.knowledge_base else 0
            self.stdout.write(f'  ✅ Analyzer initialized: {conditions_count} conditions')
        except Exception as e:
            self.stdout.write(f'  ❌ Analyzer initialization failed: {e}')

        # Initialize chatbot engine
        try:
            engine = ChatbotEngine()
            self.stdout.write('  ✅ Chatbot engine initialized')
        except Exception as e:
            self.stdout.write(f'  ❌ Chatbot engine initialization failed: {e}')

        # Warm up cache
        try:
            cache.set('system_initialized', True, 60 * 60)
            self.stdout.write('  ✅ Cache warmed up')
        except Exception as e:
            self.stdout.write(f'  ❌ Cache warm-up failed: {e}')

    def run_test_analysis(self):
        """Run test analysis with sample symptoms"""
        self.stdout.write('🧪 Running test analysis...')

        test_cases = [
            {
                'name': 'Flu-like symptoms',
                'inputs': {
                    'primary_symptoms': ['fever', 'body aches'],
                    'severity': 7,
                    'duration': '3 days',
                    'additional_symptoms': ['fatigue', 'chills']
                }
            },
            {
                'name': 'Cold-like symptoms',
                'inputs': {
                    'primary_symptoms': ['runny nose', 'sneezing'],
                    'severity': 4,
                    'duration': '5 days',
                    'additional_symptoms': ['sore throat']
                }
            },
            {
                'name': 'COVID-like symptoms',
                'inputs': {
                    'primary_symptoms': ['fever', 'dry cough'],
                    'severity': 6,
                    'duration': '4 days',
                    'additional_symptoms': ['loss of taste']
                }
            },
            {
                'name': 'Allergy symptoms',
                'inputs': {
                    'primary_symptoms': ['sneezing', 'itchy eyes'],
                    'severity': 3,
                    'duration': 'recurring episodes',
                    'additional_symptoms': ['runny nose']
                }
            }
        ]

        try:
            analyzer = EnhancedSymptomAnalyzer()

            for test_case in test_cases:
                self.stdout.write(f'\n  🧪 Testing: {test_case["name"]}')

                result = analyzer.analyze_symptoms_advanced(test_case['inputs'])

                if result and result.get('most_likely'):
                    condition = result['most_likely']['name']
                    confidence = result['most_likely']['confidence']
                    self.stdout.write(f'    Result: {condition} ({confidence:.2f} confidence)')
                else:
                    self.stdout.write('    Result: No clear diagnosis')

                # Test chatbot conversation flow
                engine = ChatbotEngine()
                session_id = f"test_{test_case['name'].replace(' ', '_')}"

                conv_result = engine.process_conversation_step(
                    step='primary_symptoms',
                    inputs=test_case['inputs'],
                    session_id=session_id
                )

                if conv_result.get('next_step'):
                    self.stdout.write(f'    Chatbot: Next step -> {conv_result["next_step"]}')

        except Exception as e:
            self.stdout.write(f'❌ Test analysis failed: {e}')

    def display_system_status(self):
        """Display current system status"""
        self.stdout.write('\n📊 System Status:')

        # Database statistics
        try:
            conditions = MedicalCondition.objects.count()
            symptoms = Symptom.objects.count()
            relationships = ConditionSymptom.objects.count()
            recommendations = SpecialistRecommendation.objects.count()

            self.stdout.write(f'  Database: {conditions} conditions, {symptoms} symptoms')
            self.stdout.write(f'  Relationships: {relationships}, Recommendations: {recommendations}')
        except Exception as e:
            self.stdout.write(f'  Database: Error - {e}')

        # Knowledge base status
        try:
            analyzer = EnhancedSymptomAnalyzer()
            if analyzer.knowledge_base:
                kb_conditions = len(analyzer.knowledge_base.get('conditions', {}))
                kb_version = analyzer.knowledge_base.get('metadata', {}).get('version', 'Unknown')
                self.stdout.write(f'  Knowledge Base: {kb_conditions} conditions (v{kb_version})')
            else:
                self.stdout.write('  Knowledge Base: Not loaded')
        except Exception as e:
            self.stdout.write(f'  Knowledge Base: Error - {e}')

        # Cache status
        try:
            if cache.get('system_initialized'):
                self.stdout.write('  Cache: Active')
            else:
                self.stdout.write('  Cache: Not initialized')
        except Exception as e:
            self.stdout.write(f'  Cache: Error - {e}')

            # Display final system status
            self.display_system_status()