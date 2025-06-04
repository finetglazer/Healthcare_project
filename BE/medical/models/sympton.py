from django.db import models

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

