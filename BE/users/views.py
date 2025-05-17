# BE/users/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .serializers import UserRegistrationSerializer, LoginSerializer, UserSerializer, DoctorSerializer, PatientSerializer
from .models import User, Doctor, Patient
from rest_framework.permissions import AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Add this line

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Prepare response data
            response_data = UserSerializer(user).data

            # Add profile data if available
            if user.is_doctor and hasattr(user, 'doctor_profile'):
                response_data['doctor_profile'] = DoctorSerializer(user.doctor_profile).data

            if user.is_patient and hasattr(user, 'patient_profile'):
                response_data['patient_profile'] = PatientSerializer(user.patient_profile).data

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)

            # Prepare response data
            response_data = UserSerializer(user).data

            # Add profile data if available
            if user.is_doctor and hasattr(user, 'doctor_profile'):
                response_data['doctor_profile'] = DoctorSerializer(user.doctor_profile).data

            if user.is_patient and hasattr(user, 'patient_profile'):
                response_data['patient_profile'] = PatientSerializer(user.patient_profile).data

            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            response_data = UserSerializer(request.user).data

            # Add profile data if available
            if request.user.is_doctor and hasattr(request.user, 'doctor_profile'):
                response_data['doctor_profile'] = DoctorSerializer(request.user.doctor_profile).data

            if request.user.is_patient and hasattr(request.user, 'patient_profile'):
                response_data['patient_profile'] = PatientSerializer(request.user.patient_profile).data

            return Response(response_data)
        return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)