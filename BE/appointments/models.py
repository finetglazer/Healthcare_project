# BE/appointments/models.py
from django.db import models
from users.models import Doctor, Patient

class Schedule(models.Model):
    doctor = models.ForeignKey('users.Doctor', on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )

    patient = models.ForeignKey('users.Patient', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('users.Doctor', on_delete=models.CASCADE, related_name='appointments')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField(blank=True)