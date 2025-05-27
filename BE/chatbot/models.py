# Medical Knowledge Base Schema for 4 Conditions

## Django Models (BE/chatbot/models.py)


from django.db import models

class MedicalCondition(models.Model):
    name = models.CharField(max_length=100)  # Flu, Cold, COVID-19, Allergy
    description = models.TextField()
    severity_level = models.CharField(max_length=20, choices=[
        ('MILD', 'Mild'),
        ('MODERATE', 'Moderate'),
        ('SEVERE', 'Severe')
    ], default='MILD')
    recommended_action = models.TextField()
    source_websites = models.JSONField(default=list)  # Store source URLs
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Symptom(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_common = models.BooleanField(default=False)  # Common symptoms appear first
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ConditionSymptom(models.Model):
    condition = models.ForeignKey(MedicalCondition, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    probability = models.FloatField(help_text="0.0 to 1.0 - how likely this symptom indicates this condition")
    is_primary = models.BooleanField(default=False)  # Key distinguishing symptoms

    class Meta:
        unique_together = ('condition', 'symptom')

class SpecialistRecommendation(models.Model):
    condition = models.ForeignKey(MedicalCondition, on_delete=models.CASCADE)
    specialist_type = models.CharField(max_length=100)  # "General Practitioner", "ENT", etc.
    urgency_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Can wait'),
        ('MEDIUM', 'See doctor soon'),
        ('HIGH', 'See doctor immediately')
    ])
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.condition.name} -> {self.specialist_type}"

## Sample Data Structure


# {
#     "conditions": [
#         {
#             "name": "Flu",
#             "symptoms": [
#                 {"name": "fever", "probability": 0.9, "is_primary": true},
#                 {"name": "body_aches", "probability": 0.8, "is_primary": true},
#                 {"name": "fatigue", "probability": 0.7, "is_primary": false}
#             ],
#             "specialists": [
#                 {"type": "General Practitioner", "urgency": "MEDIUM"}
#             ]
#         },
#         {
#             "name": "Cold",
#             "symptoms": [
#                 {"name": "runny_nose", "probability": 0.9, "is_primary": true},
#                 {"name": "sneezing", "probability": 0.8, "is_primary": true},
#                 {"name": "mild_cough", "probability": 0.6, "is_primary": false}
#             ]
#         }
#     ]
# }
