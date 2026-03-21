from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('title', 'message', 'notification_type')
        }),
        ('Recipients', {
            'fields': ('recipient',)
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Action', {
            'fields': ('action_url',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )