from django.db import models
from .condition import MedicalCondition  # Add this import


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