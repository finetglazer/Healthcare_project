# Remove duplicate model definitions, just import
from shared.models.base import User, Doctor, Patient

# Re-export for convenience
__all__ = ['User', 'Doctor', 'Patient']