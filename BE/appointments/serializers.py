# BE/appointments/serializers.py
from rest_framework import serializers
from .models import Schedule, Appointment
from users.serializers import UserSerializer, DoctorSerializer, PatientSerializer

class ScheduleSerializer(serializers.ModelSerializer):
    doctor_details = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id', 'doctor', 'date', 'start_time', 'end_time', 'slot_duration', 'is_available', 'doctor_details']
        read_only_fields = ['doctor_details']

    def get_doctor_details(self, obj):
        return {
            'name': f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}",
            'specialization': obj.doctor.specialization
        }

class AppointmentSerializer(serializers.ModelSerializer):
    patient_details = serializers.SerializerMethodField()
    doctor_details = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'schedule', 'date', 'time', 'end_time', 'status', 'reason',
                  'patient_details', 'doctor_details']
        read_only_fields = ['patient_details', 'doctor_details']

    def get_patient_details(self, obj):
        return {
            'name': f"{obj.patient.user.first_name} {obj.patient.user.last_name}",
            'email': obj.patient.user.email,
            'phone': obj.patient.user.phone_number
        }

    def get_doctor_details(self, obj):
        return {
            'name': f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}",
            'specialization': obj.doctor.specialization
        }