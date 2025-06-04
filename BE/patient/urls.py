from django.urls import path
from .views import booking, appointments

urlpatterns = [
    # Doctor discovery and booking
    path('doctors/', booking.DoctorListView.as_view(), name='doctor-list'),
    path('doctors/<int:doctor_id>/schedules/', booking.DoctorScheduleView.as_view(), name='doctor-schedules'),
    path('book/', booking.BookAppointmentView.as_view(), name='book-appointment'),

    # Patient appointments
    path('appointments/', appointments.PatientAppointmentListView.as_view(), name='patient-appointments'),
    path('appointments/<int:appointment_id>/cancel/', appointments.CancelAppointmentView.as_view(), name='cancel-appointment'),
]