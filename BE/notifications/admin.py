from django.contrib import admin
from .models import Notification, NotificationTemplate, NotificationPreference, NotificationLog

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'priority', 'is_read', 'is_delivered', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'is_delivered', 'delivery_method']
    search_fields = ['title', 'recipient__first_name', 'recipient__last_name']

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'notification_type', 'priority', 'is_active']
    list_filter = ['template_type', 'notification_type', 'priority', 'is_active']
    search_fields = ['name', 'template_type']

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'appointment_reminders', 'lab_results', 'billing_notifications']
    search_fields = ['user__first_name', 'user__last_name']

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['notification', 'delivery_method', 'status', 'attempted_at', 'delivered_at']
    list_filter = ['delivery_method', 'status', 'attempted_at']
    search_fields = ['notification__title', 'recipient_address']