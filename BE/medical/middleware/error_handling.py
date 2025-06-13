# BE/medical/middleware/error_handling.py
import logging
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from rest_framework import status

logger = logging.getLogger(__name__)

class ChatbotErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware for handling chatbot-specific errors gracefully
    """

    def process_exception(self, request, exception):
        """
        Handle exceptions in chatbot endpoints with graceful fallbacks
        """
        # Only handle requests to chatbot endpoints
        if not request.path.startswith('/api/medical/chatbot/'):
            return None

        # Log the error
        logger.error(f"Chatbot error in {request.path}: {exception}", exc_info=True)

        # Increment error counter for monitoring
        error_key = f"chatbot_errors_{request.path.replace('/', '_')}"
        current_count = cache.get(error_key, 0)
        cache.set(error_key, current_count + 1, 60 * 60)  # Track for 1 hour

        # Determine error type and provide appropriate response
        if 'analyze' in request.path:
            return self.handle_analysis_error(request, exception)
        elif 'knowledge' in request.path:
            return self.handle_knowledge_error(request, exception)
        elif 'validate' in request.path:
            return self.handle_validation_error(request, exception)
        else:
            return self.handle_generic_chatbot_error(request, exception)

    def handle_analysis_error(self, request, exception):
        """Handle analysis endpoint errors"""
        fallback_response = {
            'error': True,
            'message': 'Unable to analyze symptoms at this time. Please consult a healthcare provider.',
            'fallback_recommendation': {
                'specialist': 'General Practitioner',
                'urgency': 'MEDIUM',
                'notes': 'System temporarily unavailable. Please seek medical advice for proper diagnosis.',
                'disclaimer': 'This is a fallback recommendation due to technical issues.'
            },
            'next_steps': [
                'Consult a healthcare provider',
                'Keep track of your symptoms',
                'Seek immediate care if symptoms worsen'
            ],
            'technical_error': str(exception) if logger.isEnabledFor(logging.DEBUG) else None
        }

        return JsonResponse(fallback_response, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def handle_knowledge_error(self, request, exception):
        """Handle knowledge base endpoint errors"""
        fallback_response = {
            'error': True,
            'message': 'Medical knowledge base temporarily unavailable.',
            'fallback_data': {
                'conditions': {
                    'flu': {'name': 'Influenza', 'description': 'Viral respiratory illness'},
                    'cold': {'name': 'Common Cold', 'description': 'Upper respiratory infection'},
                    'covid-19': {'name': 'COVID-19', 'description': 'Coronavirus disease'},
                    'allergy': {'name': 'Allergic Reaction', 'description': 'Immune response to allergens'}
                },
                'note': 'Limited data available due to technical issues'
            }
        }

        return JsonResponse(fallback_response, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def handle_validation_error(self, request, exception):
        """Handle validation endpoint errors"""
        fallback_response = {
            'error': True,
            'message': 'Symptom validation temporarily unavailable.',
            'fallback_validation': {
                'all_symptoms_accepted': True,
                'note': 'Unable to validate symptoms against knowledge base. All inputs accepted.',
                'recommendation': 'Please consult healthcare provider for accurate symptom assessment.'
            }
        }

        return JsonResponse(fallback_response, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def handle_generic_chatbot_error(self, request, exception):
        """Handle generic chatbot errors"""
        fallback_response = {
            'error': True,
            'message': 'Chatbot service temporarily unavailable.',
            'fallback_message': 'Please consult a healthcare provider for medical advice.',
            'emergency_contacts': {
                'emergency': '911',
                'poison_control': '1-800-222-1222',
                'note': 'Call emergency services if experiencing severe symptoms'
            }
        }

        return JsonResponse(fallback_response, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class ChatbotRateLimitingMiddleware(MiddlewareMixin):
    """
    Simple rate limiting for chatbot endpoints to prevent abuse
    """

    def process_request(self, request):
        """
        Apply rate limiting to chatbot endpoints
        """
        if not request.path.startswith('/api/medical/chatbot/'):
            return None

        # Get client IP
        client_ip = self.get_client_ip(request)

        # Check rate limit
        rate_key = f"chatbot_rate_limit_{client_ip}"
        current_requests = cache.get(rate_key, 0)

        # Allow 60 requests per hour per IP
        if current_requests >= 60:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please wait before trying again.',
                'retry_after': 3600,  # 1 hour
                'contact': 'Please contact support if you need higher limits for legitimate use.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Increment counter
        cache.set(rate_key, current_requests + 1, 60 * 60)  # 1 hour window

        return None

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ChatbotLoggingMiddleware(MiddlewareMixin):
    """
    Enhanced logging for chatbot requests
    """

    def process_request(self, request):
        """Log chatbot requests for monitoring"""
        if request.path.startswith('/api/medical/chatbot/'):
            # Log request details (be careful with sensitive data)
            log_data = {
                'path': request.path,
                'method': request.method,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'timestamp': str(timezone.now()),
                'session_id': self.extract_session_id(request)
            }

            logger.info(f"Chatbot request: {json.dumps(log_data)}")

    def process_response(self, request, response):
        """Log chatbot responses"""
        if request.path.startswith('/api/medical/chatbot/'):
            log_data = {
                'path': request.path,
                'status_code': response.status_code,
                'response_size': len(response.content) if hasattr(response, 'content') else 0
            }

            if response.status_code >= 400:
                logger.warning(f"Chatbot error response: {json.dumps(log_data)}")
            else:
                logger.info(f"Chatbot response: {json.dumps(log_data)}")

        return response

    def extract_session_id(self, request):
        """Extract session ID from request for tracking"""
        try:
            if hasattr(request, 'data') and 'session_id' in request.data:
                return request.data['session_id']
            elif request.GET.get('session_id'):
                return request.GET.get('session_id')
        except:
            pass
        return None


# Import timezone
from django.utils import timezone