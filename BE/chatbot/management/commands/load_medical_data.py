from django.core.management.base import BaseCommand
from chatbot.models import MedicalCondition, Symptom, ConditionSymptom, SpecialistRecommendation

class Command(BaseCommand):
    help = 'Load sample medical data for 4 conditions'

    def handle(self, *args, **options):
        # Create conditions
        flu = MedicalCondition.objects.create(
            name='Flu',
            description='Seasonal influenza caused by influenza viruses',
            severity_level='MODERATE',
            recommended_action='Rest, fluids, and antiviral medication if needed'
        )

        cold = MedicalCondition.objects.create(
            name='Cold',
            description='Common cold caused by various viruses',
            severity_level='MILD',
            recommended_action='Rest, fluids, and symptom management'
        )

        covid = MedicalCondition.objects.create(
            name='COVID-19',
            description='Coronavirus disease caused by SARS-CoV-2',
            severity_level='MODERATE',
            recommended_action='Isolation, monitoring, and medical care if symptoms worsen'
        )

        allergy = MedicalCondition.objects.create(
            name='Allergy',
            description='Allergic reactions to environmental triggers',
            severity_level='MILD',
            recommended_action='Avoid triggers and use antihistamines'
        )

        # Create symptoms
        symptoms_data = [
            ('fever', 'Elevated body temperature', True),
            ('cough', 'Persistent coughing', True),
            ('runny_nose', 'Nasal discharge', True),
            ('body_aches', 'Muscle and body pain', False),
            ('fatigue', 'Tiredness and weakness', True),
            ('sore_throat', 'Throat pain and irritation', True),
            ('headache', 'Head pain', True),
            ('loss_of_taste', 'Unable to taste food', False),
            ('loss_of_smell', 'Unable to smell', False),
            ('sneezing', 'Frequent sneezing', False),
            ('difficulty_breathing', 'Shortness of breath', False),
        ]

        symptoms = {}
        for name, desc, is_common in symptoms_data:
            symptom = Symptom.objects.create(
                name=name,
                description=desc,
                is_common=is_common
            )
            symptoms[name] = symptom

        # Create condition-symptom relationships
        # Flu
        flu_symptoms = [
            ('fever', 0.9, True),
            ('body_aches', 0.8, True),
            ('fatigue', 0.7, False),
            ('cough', 0.6, False),
            ('headache', 0.6, False),
        ]

        for symptom_name, prob, is_primary in flu_symptoms:
            ConditionSymptom.objects.create(
                condition=flu,
                symptom=symptoms[symptom_name],
                probability=prob,
                is_primary=is_primary
            )

        # Cold
        cold_symptoms = [
            ('runny_nose', 0.9, True),
            ('sneezing', 0.8, True),
            ('sore_throat', 0.7, False),
            ('cough', 0.6, False),
        ]

        for symptom_name, prob, is_primary in cold_symptoms:
            ConditionSymptom.objects.create(
                condition=cold,
                symptom=symptoms[symptom_name],
                probability=prob,
                is_primary=is_primary
            )

        # COVID-19
        covid_symptoms = [
            ('fever', 0.7, True),
            ('cough', 0.8, True),
            ('loss_of_taste', 0.8, True),
            ('loss_of_smell', 0.8, True),
            ('fatigue', 0.6, False),
            ('difficulty_breathing', 0.4, False),
        ]

        for symptom_name, prob, is_primary in covid_symptoms:
            ConditionSymptom.objects.create(
                condition=covid,
                symptom=symptoms[symptom_name],
                probability=prob,
                is_primary=is_primary
            )

        # Allergy
        allergy_symptoms = [
            ('sneezing', 0.9, True),
            ('runny_nose', 0.8, True),
            ('fatigue', 0.4, False),
        ]

        for symptom_name, prob, is_primary in allergy_symptoms:
            ConditionSymptom.objects.create(
                condition=allergy,
                symptom=symptoms[symptom_name],
                probability=prob,
                is_primary=is_primary
            )

        # Create specialist recommendations
        recommendations = [
            (flu, 'General Practitioner', 'MEDIUM', 'Monitor symptoms and rest'),
            (cold, 'General Practitioner', 'LOW', 'Home remedies and rest'),
            (covid, 'General Practitioner', 'HIGH', 'Get tested and isolate'),
            (allergy, 'Allergist', 'LOW', 'Consider allergy testing'),
        ]

        for condition, specialist, urgency, notes in recommendations:
            SpecialistRecommendation.objects.create(
                condition=condition,
                specialist_type=specialist,
                urgency_level=urgency,
                notes=notes
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully loaded medical data for 4 conditions')
        )