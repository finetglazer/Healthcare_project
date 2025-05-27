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

    def __str__(self):
        return f"{self.condition.name} - {self.symptom.name}"

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