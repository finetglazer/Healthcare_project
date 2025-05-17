# BE/users/serializers.py
from rest_framework import serializers
from .models import User, Doctor, Patient
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'is_doctor', 'is_patient')

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'specialization')

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'date_of_birth')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    specialization = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name',
                  'phone_number', 'is_doctor', 'is_patient', 'specialization', 'date_of_birth')

    def create(self, validated_data):
        # Extract extra fields that aren't part of the User model
        specialization = validated_data.pop('specialization', '')
        date_of_birth = validated_data.pop('date_of_birth', None)

        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            is_doctor=validated_data.get('is_doctor', False),
            is_patient=validated_data.get('is_patient', False)
        )

        # Create associated profile based on user type
        if user.is_doctor:
            Doctor.objects.create(user=user, specialization=specialization)

        if user.is_patient:
            Patient.objects.create(user=user, date_of_birth=date_of_birth)

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid username or password.")