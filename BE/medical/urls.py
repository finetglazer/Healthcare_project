# BE/medical/urls.py
from django.urls import path
from .views import analysis, knowledge, chatbot

urlpatterns = [
    # Original endpoints
    path('analyze/', analysis.SymptomAnalysisView.as_view(), name='symptom-analysis'),
    path('knowledge/', knowledge.MedicalKnowledgeView.as_view(), name='medical-knowledge'),

    # Enhanced chatbot endpoints for Phase 1
    path('chatbot/analyze/', chatbot.ChatbotAnalysisView.as_view(), name='chatbot-analysis'),
    path('chatbot/knowledge/', chatbot.KnowledgeBaseView.as_view(), name='chatbot-knowledge'),
    path('chatbot/validate/', chatbot.SymptomValidationView.as_view(), name='symptom-validation'),

    # Additional utility endpoints
    path('conditions/', knowledge.MedicalConditionsListView.as_view(), name='conditions-list'),
    path('conditions/<str:condition_key>/', knowledge.MedicalConditionDetailView.as_view(), name='condition-detail'),
    path('symptoms/search/', knowledge.SymptomSearchView.as_view(), name='symptom-search'),

    # Analytics and feedback endpoints (for future use)
    path('chatbot/feedback/', chatbot.ChatbotFeedbackView.as_view(), name='chatbot-feedback'),
    path('chatbot/session/<str:session_id>/', chatbot.ConversationSessionView.as_view(), name='conversation-session'),
]