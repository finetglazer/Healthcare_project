from django.urls import path
from .views import analysis, knowledge

urlpatterns = [
    path('analyze/', analysis.SymptomAnalysisView.as_view(), name='symptom-analysis'),
    path('knowledge/', knowledge.MedicalKnowledgeView.as_view(), name='medical-knowledge'),
]