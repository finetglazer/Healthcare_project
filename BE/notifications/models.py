# BE/notifications/models.py.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('APPOINTMENT', 'Appointment'),
        ('PRESCRIPTION', 'Prescription'),
        ('LAB_RESULT', 'Lab Result'),
        ('BILLING', 'Billing'),
        ('SYSTEM', 'System'),
        ('REMINDER', 'Reminder'),
        ('ALERT', 'Alert'),
        ('MESSAGE', 'Message'),
        ('EMERGENCY', 'Emergency'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
        ('CRITICAL', 'Critical'),
    ]

    DELIVERY_METHOD_CHOICES = [
        ('IN_APP', 'In-App Notification'),
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('PHONE', 'Phone Call'),
    ]

    # Basic Information
    recipient = models.ForeignKey('shared.User', on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey('shared.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')

    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    action_url = models.URLField(blank=True, help_text="URL to navigate when notification is clicked")
    action_text = models.CharField(max_length=100, blank=True, help_text="Text for action button")

    # Related Object (Generic Foreign Key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    # Status and Delivery
    is_read = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHOD_CHOICES, default='IN_APP')
    delivery_attempts = models.PositiveIntegerField(default=0)
    last_delivery_attempt = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True, help_text="When to send this notification")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When this notification expires")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional data for notification")

    def __str__(self):
        return f"{self.notification_type} - {self.title} to {self.recipient.get_full_name()}"

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['scheduled_for']),
        ]

class NotificationTemplate(models.Model):
    """Templates for common notifications"""
    TEMPLATE_TYPE_CHOICES = [
        ('APPOINTMENT_REMINDER', 'Appointment Reminder'),
        ('APPOINTMENT_CONFIRMATION', 'Appointment Confirmation'),
        ('APPOINTMENT_CANCELLATION', 'Appointment Cancellation'),
        ('LAB_RESULT_READY', 'Lab Result Ready'),
        ('PRESCRIPTION_READY', 'Prescription Ready'),
        ('BILL_GENERATED', 'Bill Generated'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('MEDICATION_REMINDER', 'Medication Reminder'),
        ('FOLLOW_UP_REMINDER', 'Follow-up Reminder'),
        ('WELCOME_MESSAGE', 'Welcome Message'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('EMERGENCY_ALERT', 'Emergency Alert'),
    ]

    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPE_CHOICES, unique=True)
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_CHOICES, default='NORMAL')

    # Template Content
    title_template = models.CharField(max_length=200, help_text="Use {variable} for dynamic content")
    message_template = models.TextField(help_text="Use {variable} for dynamic content")
    action_text = models.CharField(max_length=100, blank=True)
    action_url_template = models.CharField(max_length=500, blank=True)

    # Delivery Settings
    delivery_methods = models.JSONField(
        default=list,
        help_text="List of delivery methods: ['IN_APP', 'EMAIL', 'SMS']"
    )
    send_immediately = models.BooleanField(default=True)
    delay_minutes = models.PositiveIntegerField(default=0, help_text="Delay before sending")

    # Template variables documentation
    available_variables = models.JSONField(
        default=list,
        help_text="List of available variables for this template"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.template_type})"

    class Meta:
        db_table = 'notification_templates'

class NotificationPreference(models.Model):
    """User preferences for different types of notifications"""
    user = models.OneToOneField('shared.User', on_delete=models.CASCADE, related_name='notification_preferences')

    # Appointment Notifications
    appointment_reminders = models.BooleanField(default=True)
    appointment_confirmations = models.BooleanField(default=True)
    appointment_cancellations = models.BooleanField(default=True)
    appointment_delivery_methods = models.JSONField(default=lambda: ['IN_APP', 'EMAIL'])

    # Medical Notifications
    lab_results = models.BooleanField(default=True)
    prescription_ready = models.BooleanField(default=True)
    medication_reminders = models.BooleanField(default=True)
    medical_delivery_methods = models.JSONField(default=lambda: ['IN_APP', 'EMAIL'])

    # Billing Notifications
    billing_notifications = models.BooleanField(default=True)
    payment_confirmations = models.BooleanField(default=True)
    billing_delivery_methods = models.JSONField(default=lambda: ['IN_APP', 'EMAIL'])

    # System Notifications
    system_updates = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    system_delivery_methods = models.JSONField(default=lambda: ['IN_APP'])

    # Emergency Notifications (cannot be disabled)
    emergency_alerts = models.BooleanField(default=True, editable=False)
    emergency_delivery_methods = models.JSONField(default=lambda: ['IN_APP', 'EMAIL', 'SMS', 'PUSH'])

    # General Settings
    do_not_disturb_start = models.TimeField(null=True, blank=True, help_text="Start of quiet hours")
    do_not_disturb_end = models.TimeField(null=True, blank=True, help_text="End of quiet hours")
    timezone = models.CharField(max_length=50, default='UTC')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification preferences for {self.user.get_full_name()}"

    class Meta:
        db_table = 'notification_preferences'

class NotificationLog(models.Model):
    """Log of all notification delivery attempts"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
        ('SPAM', 'Marked as Spam'),
    ]

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='delivery_logs')
    delivery_method = models.CharField(max_length=10, choices=Notification.DELIVERY_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    # Delivery Details
    recipient_address = models.CharField(max_length=200, help_text="Email, phone number, etc.")
    provider = models.CharField(max_length=100, blank=True, help_text="Email service, SMS provider, etc.")
    external_id = models.CharField(max_length=200, blank=True, help_text="Provider's message ID")

    # Response Data
    response_code = models.CharField(max_length=20, blank=True)
    response_message = models.TextField(blank=True)
    error_details = models.TextField(blank=True)

    # Timing
    attempted_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Cost tracking (if applicable)
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"{self.delivery_method} delivery of notification {self.notification.id} - {self.status}"

    class Meta:
        db_table = 'notification_logs'
        ordering = ['-attempted_at']