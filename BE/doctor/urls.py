from django.urls import path
from .views import schedule, appointments

urlpatterns = [
    # Schedule management
    path('schedules/', schedule.DoctorScheduleListCreateView.as_view(), name='doctor-schedules'),
    path('schedules/<int:pk>/', schedule.DoctorScheduleDetailView.as_view(), name='doctor-schedule-detail'),

    # Appointments
    path('appointments/', appointments.DoctorAppointmentListView.as_view(), name='doctor-appointments'),
]