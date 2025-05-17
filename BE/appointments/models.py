# BE/appointments/models.py (update)
from django.db import models
from users.models import Doctor, Patient

class Schedule(models.Model):
    DURATION_CHOICES = (
        (30, '30 minutes'),
        (60, '1 hour'),
        (90, '1 hour 30 minutes'),
        (120, '2 hours'),
    )

    doctor = models.ForeignKey('users.Doctor', on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.IntegerField(choices=DURATION_CHOICES, default=30)
    is_available = models.BooleanField(default=True)

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )

    patient = models.ForeignKey('users.Patient', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('users.Doctor', on_delete=models.CASCADE, related_name='appointments')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    end_time = models.TimeField()  # Added end_time
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    reason = models.TextField()  # Made required