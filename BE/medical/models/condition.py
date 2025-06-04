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
