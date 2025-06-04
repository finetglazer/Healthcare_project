from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('shared.authentication.urls')),
    path('api/doctor/', include('doctor.urls')),
    path('api/patient/', include('patient.urls')),
    path('api/medical/', include('medical.urls')),
]