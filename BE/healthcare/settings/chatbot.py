# BE/healthcare/settings/chatbot.py
# Chatbot-specific Django settings to be imported in main settings.py

import os
from pathlib import Path

# Chatbot System Configuration
CHATBOT_CONFIG = {
    # Knowledge Base Settings
    'KNOWLEDGE_BASE_DIR': 'medical_knowledge',
    'KNOWLEDGE_BASE_CACHE_TIMEOUT': 60 * 30,  # 30 minutes
    'REBUILD_KB_ON_STARTUP': False,

    # Conversation Settings
    'MAX_CONVERSATION_DURATION': 60 * 60 * 2,  # 2 hours
    'SESSION_CLEANUP_INTERVAL': 60 * 60,  # 1 hour
    'MAX_SYMPTOMS_PER_REQUEST': 20,
    'MIN_CONFIDENCE_THRESHOLD': 0.3,

    # Analysis Settings
    'ENABLE_DIFFERENTIAL_DIAGNOSIS': True,
    'ENABLE_URGENCY_DETECTION': True,
    'FALLBACK_TO_SIMPLE_ANALYSIS': True,
    'MAX_CONDITIONS_IN_RESULT': 5,

    # Rate Limiting
    'RATE_LIMIT_REQUESTS_PER_HOUR': 60,
    'RATE_LIMIT_BURST_ALLOWANCE': 10,
    'ENABLE_RATE_LIMITING': True,

    # Error Handling
    'LOG_ALL_REQUESTS': True,
    'LOG_ERRORS_ONLY': False,
    'ENABLE_FALLBACK_RESPONSES': True,
    'GRACEFUL_DEGRADATION': True,

    # Medical Safety
    'ENABLE_MEDICAL_DISCLAIMERS': True,
    'URGENT_SYMPTOMS_THRESHOLD': 8,
    'REQUIRE_DISCLAIMER_ACCEPTANCE': True,
    'EMERGENCY_CONTACT_INFO': {
        'emergency': '911',
        'poison_control': '1-800-222-1222',
        'mental_health': '988'
    },

    # Data Validation
    'STRICT_SYMPTOM_VALIDATION': True,
    'CONTENT_FILTERING_ENABLED': True,
    'MAX_SYMPTOM_LENGTH': 200,
    'BLOCKED_TERMS': [
        'suicide', 'self-harm', 'overdose', 'illegal drug',
        'recreational drug', 'substance abuse'
    ]
}

# Enhanced Caching Configuration for Chatbot
CHATBOT_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'chatbot-cache',
        'TIMEOUT': 60 * 15,  # 15 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCY': 3,
        }
    },
    'knowledge_base': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'kb-cache',
        'TIMEOUT': 60 * 60,  # 1 hour for knowledge base
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 4,
        }
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'session-cache',
        'TIMEOUT': 60 * 60 * 2,  # 2 hours for sessions
        'OPTIONS': {
            'MAX_ENTRIES': 5000,
            'CULL_FREQUENCY': 2,
        }
    }
}

# Logging Configuration for Chatbot
CHATBOT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'chatbot_formatter': {
            'format': '[{levelname}] {asctime} - Chatbot - {name}: {message}',
            'style': '{',
        },
        'detailed_formatter': {
            'format': '[{levelname}] {asctime} - {name} - {pathname}:{lineno} - {message}',
            'style': '{',
        }
    },
    'handlers': {
        'chatbot_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(Path(__file__).parent.parent.parent, 'logs', 'chatbot.log'),
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'chatbot_formatter',
        },
        'chatbot_error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(Path(__file__).parent.parent.parent, 'logs', 'chatbot_errors.log'),
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 3,
            'formatter': 'detailed_formatter',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'chatbot_formatter',
        }
    },
    'loggers': {
        'medical.services.enhanced_analyzer': {
            'handlers': ['chatbot_file', 'chatbot_error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'medical.services.chatbot_engine': {
            'handlers': ['chatbot_file', 'chatbot_error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'medical.views.chatbot': {
            'handlers': ['chatbot_file', 'chatbot_error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'medical.middleware.error_handling': {
            'handlers': ['chatbot_error_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        }
    }
}

# Middleware Configuration
CHATBOT_MIDDLEWARE = [
    'medical.middleware.error_handling.ChatbotRateLimitingMiddleware',
    'medical.middleware.error_handling.ChatbotLoggingMiddleware',
    'medical.middleware.error_handling.ChatbotErrorHandlingMiddleware',
]

# REST Framework Configuration for Chatbot
CHATBOT_REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/hour',
        'user': '120/hour',
        'chatbot': '60/hour'
    }
}

# File Upload Settings for Medical Documents
CHATBOT_FILE_UPLOAD = {
    'MAX_UPLOAD_SIZE': 1024 * 1024 * 5,  # 5MB
    'ALLOWED_EXTENSIONS': ['.txt', '.pdf', '.doc', '.docx'],
    'UPLOAD_PATH': 'medical_uploads/',
    'SCAN_UPLOADS': True,  # Scan for malicious content
}

# API Documentation Settings
CHATBOT_API_DOCS = {
    'TITLE': 'Medical Chatbot API',
    'DESCRIPTION': 'API for medical symptom analysis and chatbot interactions',
    'VERSION': '1.0.0',
    'PUBLIC_API': False,
    'INCLUDE_SCHEMA': True,
}

# Development/Testing Settings
CHATBOT_DEVELOPMENT = {
    'ENABLE_DEBUG_MODE': False,
    'MOCK_KNOWLEDGE_BASE': False,
    'SIMULATE_ERRORS': False,
    'TEST_SESSION_ID': 'test_session_12345',
    'BYPASS_RATE_LIMITING': False,
}

# Production Settings
CHATBOT_PRODUCTION = {
    'ENABLE_MONITORING': True,
    'HEALTH_CHECK_ENDPOINT': '/api/medical/chatbot/health/',
    'METRICS_COLLECTION': True,
    'PERFORMANCE_TRACKING': True,
    'ERROR_ALERTING': True,
    'BACKUP_KNOWLEDGE_BASE': True,
}

# Integration Settings
CHATBOT_INTEGRATIONS = {
    'ENABLE_EXTERNAL_APIS': False,
    'MEDICAL_DATABASE_SYNC': False,
    'THIRD_PARTY_VALIDATION': False,
    'EXTERNAL_KNOWLEDGE_SOURCES': [],
}

# Security Settings
CHATBOT_SECURITY = {
    'ENCRYPT_SESSION_DATA': True,
    'ANONYMIZE_LOGS': True,
    'DATA_RETENTION_DAYS': 30,
    'GDPR_COMPLIANCE': True,
    'HIPAA_MODE': True,
    'SENSITIVE_DATA_MASKING': True,
}

# Function to merge chatbot settings with main Django settings
def configure_chatbot_settings(settings_dict):
    """
    Merge chatbot settings with main Django settings
    Usage in main settings.py:

    from .chatbot import configure_chatbot_settings
    configure_chatbot_settings(locals())
    """

    # Merge caching settings
    if 'CACHES' not in settings_dict:
        settings_dict['CACHES'] = CHATBOT_CACHES
    else:
        settings_dict['CACHES'].update(CHATBOT_CACHES)

    # Add middleware
    if 'MIDDLEWARE' in settings_dict:
        # Insert chatbot middleware before existing middleware
        for middleware in reversed(CHATBOT_MIDDLEWARE):
            if middleware not in settings_dict['MIDDLEWARE']:
                settings_dict['MIDDLEWARE'].insert(0, middleware)

    # Merge logging settings
    if 'LOGGING' not in settings_dict:
        settings_dict['LOGGING'] = CHATBOT_LOGGING
    else:
        # Merge loggers
        if 'loggers' not in settings_dict['LOGGING']:
            settings_dict['LOGGING']['loggers'] = {}
        settings_dict['LOGGING']['loggers'].update(CHATBOT_LOGGING['loggers'])

        # Merge handlers and formatters
        if 'handlers' not in settings_dict['LOGGING']:
            settings_dict['LOGGING']['handlers'] = {}
        settings_dict['LOGGING']['handlers'].update(CHATBOT_LOGGING['handlers'])

        if 'formatters' not in settings_dict['LOGGING']:
            settings_dict['LOGGING']['formatters'] = {}
        settings_dict['LOGGING']['formatters'].update(CHATBOT_LOGGING['formatters'])

    # Add chatbot-specific settings
    settings_dict['CHATBOT_CONFIG'] = CHATBOT_CONFIG
    settings_dict['CHATBOT_DEVELOPMENT'] = CHATBOT_DEVELOPMENT
    settings_dict['CHATBOT_PRODUCTION'] = CHATBOT_PRODUCTION
    settings_dict['CHATBOT_SECURITY'] = CHATBOT_SECURITY

    return settings_dict

# Environment-specific configurations
def get_chatbot_config_for_environment(environment='development'):
    """
    Get chatbot configuration for specific environment
    """
    base_config = CHATBOT_CONFIG.copy()

    if environment == 'development':
        base_config.update({
            'LOG_ALL_REQUESTS': True,
            'ENABLE_DEBUG_MODE': True,
            'RATE_LIMIT_REQUESTS_PER_HOUR': 1000,  # More lenient for dev
            'REBUILD_KB_ON_STARTUP': True,
        })
    elif environment == 'production':
        base_config.update({
            'LOG_ERRORS_ONLY': True,
            'ENABLE_MONITORING': True,
            'STRICT_SYMPTOM_VALIDATION': True,
            'RATE_LIMIT_REQUESTS_PER_HOUR': 60,
        })
    elif environment == 'testing':
        base_config.update({
            'ENABLE_DEBUG_MODE': True,
            'MOCK_KNOWLEDGE_BASE': True,
            'BYPASS_RATE_LIMITING': True,
            'SIMULATE_ERRORS': False,
        })

    return base_config