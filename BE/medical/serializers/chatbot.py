# BE/medical/serializers/chatbot.py
from rest_framework import serializers
from typing import List, Dict, Any

class ChatbotAnalysisSerializer(serializers.Serializer):
    """
    Serializer for chatbot analysis requests
    """
    conversation_step = serializers.ChoiceField(
        choices=[
            'greeting',
            'primary_symptoms',
            'severity',
            'duration',
            'additional_symptoms',
            'differential_questions',
            'analysis'
        ],
        required=True
    )

    user_inputs = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=dict
    )

    session_id = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Unique session identifier for conversation tracking"
    )

    def validate_user_inputs(self, value):
        """Validate user inputs based on conversation step"""
        conversation_step = self.initial_data.get('conversation_step')

        if conversation_step == 'primary_symptoms':
            if 'primary_symptoms' not in value:
                raise serializers.ValidationError("primary_symptoms is required for this step")

            primary_symptoms = value['primary_symptoms']
            if isinstance(primary_symptoms, str):
                # Convert string to list
                value['primary_symptoms'] = [primary_symptoms]
            elif not isinstance(primary_symptoms, list):
                raise serializers.ValidationError("primary_symptoms must be a list or string")

        elif conversation_step == 'severity':
            if 'severity' not in value:
                raise serializers.ValidationError("severity is required for this step")

            try:
                severity = int(value['severity'])
                if not 1 <= severity <= 10:
                    raise serializers.ValidationError("severity must be between 1 and 10")
                value['severity'] = severity
            except (ValueError, TypeError):
                raise serializers.ValidationError("severity must be a valid integer")

        elif conversation_step == 'duration':
            if 'duration' not in value:
                raise serializers.ValidationError("duration is required for this step")

        elif conversation_step == 'additional_symptoms':
            if 'additional_symptoms' in value:
                additional_symptoms = value['additional_symptoms']
                if isinstance(additional_symptoms, str):
                    value['additional_symptoms'] = [additional_symptoms] if additional_symptoms else []
                elif not isinstance(additional_symptoms, list):
                    raise serializers.ValidationError("additional_symptoms must be a list or string")

        elif conversation_step == 'differential_questions':
            if 'differential_answer' not in value:
                raise serializers.ValidationError("differential_answer is required for this step")

        return value

    def validate_session_id(self, value):
        """Validate session ID format"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("session_id cannot be empty")
        return value.strip()


class SymptomValidationSerializer(serializers.Serializer):
    """
    Serializer for symptom validation requests
    """
    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=200),
        min_length=1,
        max_length=20,
        help_text="List of symptoms to validate"
    )

    def validate_symptoms(self, value):
        """Validate symptom list"""
        validated_symptoms = []

        for symptom in value:
            # Clean and validate each symptom
            clean_symptom = symptom.strip()

            if len(clean_symptom) < 2:
                raise serializers.ValidationError(f"Symptom '{symptom}' is too short")

            if len(clean_symptom) > 200:
                raise serializers.ValidationError(f"Symptom '{symptom}' is too long")

            # Check for potentially harmful content
            harmful_patterns = ['drug', 'suicide', 'self-harm', 'overdose']
            if any(pattern in clean_symptom.lower() for pattern in harmful_patterns):
                raise serializers.ValidationError(f"Symptom '{symptom}' contains inappropriate content")

            validated_symptoms.append(clean_symptom)

        return validated_symptoms


class ConversationStepSerializer(serializers.Serializer):
    """
    Serializer for conversation step responses
    """
    message = serializers.CharField()
    next_step = serializers.CharField(allow_null=True)
    question = serializers.DictField(allow_null=True)
    progress = serializers.IntegerField(min_value=0, max_value=100)
    analysis_complete = serializers.BooleanField(default=False)
    error = serializers.BooleanField(default=False)

    # Optional fields
    preliminary_conditions = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    urgency_detected = serializers.BooleanField(required=False)
    differential_type = serializers.CharField(required=False)


class KnowledgeBaseSerializer(serializers.Serializer):
    """
    Serializer for knowledge base data
    """
    conditions = serializers.DictField()
    symptoms = serializers.ListField(child=serializers.DictField())
    conversation_flows = serializers.DictField()
    probability_matrix = serializers.DictField()
    metadata = serializers.DictField()


class AnalysisResultSerializer(serializers.Serializer):
    """
    Serializer for comprehensive analysis results
    """
    most_likely = serializers.DictField()
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    recommendations = serializers.ListField(child=serializers.DictField())
    all_matches = serializers.ListField(child=serializers.DictField())
    urgency = serializers.ChoiceField(
        choices=['LOW', 'MEDIUM', 'HIGH', 'URGENT']
    )
    disclaimers = serializers.ListField(child=serializers.CharField())

    # Chatbot-specific fields
    chatbot_response = serializers.DictField(required=False)
    next_steps = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer for error responses
    """
    error = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    fallback_recommendation = serializers.DictField(required=False)


# Enhanced serializers for specific medical data

class MedicalConditionDetailSerializer(serializers.Serializer):
    """
    Detailed medical condition serializer
    """
    name = serializers.CharField()
    description = serializers.CharField()
    severity_level = serializers.ChoiceField(
        choices=['MILD', 'MODERATE', 'SEVERE', 'CRITICAL']
    )
    primary_symptoms = serializers.ListField(child=serializers.CharField())
    secondary_symptoms = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    sources = serializers.ListField(
        child=serializers.URLField(),
        required=False
    )
    specialist_recommendations = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class SymptomDetailSerializer(serializers.Serializer):
    """
    Detailed symptom serializer
    """
    name = serializers.CharField()
    frequency = serializers.FloatField(min_value=0.0, max_value=1.0)
    conditions = serializers.ListField(child=serializers.CharField())
    severity_indicators = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    urgency_flags = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class ConversationHistorySerializer(serializers.Serializer):
    """
    Serializer for conversation history tracking
    """
    session_id = serializers.CharField()
    steps_completed = serializers.ListField(child=serializers.CharField())
    total_inputs = serializers.DictField()
    analysis_result = AnalysisResultSerializer(required=False)
    started_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(required=False)
    user_satisfaction = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=False
    )


class ChatbotConfigSerializer(serializers.Serializer):
    """
    Serializer for chatbot configuration
    """
    conversation_flow = serializers.ListField(child=serializers.CharField())
    skip_conditions = serializers.DictField()
    differential_questions = serializers.DictField()
    urgency_thresholds = serializers.DictField()
    medical_disclaimers = serializers.ListField(child=serializers.CharField())


# Input sanitization helpers

class SanitizedCharField(serializers.CharField):
    """
    Custom CharField with input sanitization
    """
    def to_internal_value(self, data):
        value = super().to_internal_value(data)

        # Remove potentially harmful content
        import re

        # Remove HTML tags
        value = re.sub(r'<[^>]+>', '', value)

        # Remove excessive whitespace
        value = re.sub(r'\s+', ' ', value).strip()

        # Remove special characters that could be used for injection
        value = re.sub(r'[<>"\']', '', value)

        return value


class SanitizedListField(serializers.ListField):
    """
    Custom ListField with sanitization for each item
    """
    def __init__(self, **kwargs):
        kwargs['child'] = SanitizedCharField()
        super().__init__(**kwargs)


# Validation helpers

def validate_medical_content(value):
    """
    Validate that content is appropriate for medical context
    """
    inappropriate_terms = [
        'self-harm', 'suicide', 'overdose', 'illegal drug',
        'recreational drug', 'abuse', 'addiction'
    ]

    value_lower = value.lower()
    for term in inappropriate_terms:
        if term in value_lower:
            raise serializers.ValidationError(
                f"Content contains inappropriate medical terminology: {term}"
            )

    return value


def validate_symptom_severity(value):
    """
    Validate symptom severity input
    """
    if not isinstance(value, (int, float)):
        raise serializers.ValidationError("Severity must be a number")

    if not 1 <= value <= 10:
        raise serializers.ValidationError("Severity must be between 1 and 10")

    return int(value)


def validate_session_duration(session_data):
    """
    Validate session hasn't expired or become corrupted
    """
    import datetime
    from django.utils import timezone

    if 'created_at' not in session_data:
        raise serializers.ValidationError("Invalid session data")

    # Check if session is older than 2 hours
    created_at = datetime.datetime.fromisoformat(session_data['created_at'])
    if timezone.now() - created_at > datetime.timedelta(hours=2):
        raise serializers.ValidationError("Session has expired")

    return session_data