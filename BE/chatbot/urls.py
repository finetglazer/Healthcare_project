from django.urls import path
from .views import SymptomAnalysisView, MedicalKnowledgeView

urlpatterns = [
    path('analyze/', SymptomAnalysisView.as_view(), name='symptom-analysis'),
    path('knowledge/', MedicalKnowledgeView.as_view(), name='medical-knowledge'),
]