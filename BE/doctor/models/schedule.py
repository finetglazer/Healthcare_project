# Fix: doctor/models/schedule.py

from django.db import models

class Schedule(models.Model):
    DURATION_CHOICES = (
        (30, '30 minutes'),
        (60, '1 hour'),
        (90, '1 hour 30 minutes'),
        (120, '2 hours'),
    )

    doctor = models.ForeignKey('shared.Doctor', on_delete=models.CASCADE, related_name='schedules')  # Changed from 'users.Doctor'
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.IntegerField(choices=DURATION_CHOICES, default=30)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Schedule for Dr. {self.doctor.user.last_name} on {self.date}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )

    patient = models.ForeignKey('shared.Patient', on_delete=models.CASCADE, related_name='appointments')  # Changed from 'users.Patient'
    doctor = models.ForeignKey('shared.Doctor', on_delete=models.CASCADE, related_name='appointments')    # Changed from 'users.Doctor'
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    reason = models.TextField()

    def __str__(self):
        return f"Appointment: {self.patient.user.first_name} with Dr. {self.doctor.user.last_name} on {self.date}"