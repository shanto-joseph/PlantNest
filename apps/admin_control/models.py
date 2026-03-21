from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        # Order related
        ('order_placed', 'New Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('order_status', 'Order Status Update'),
        
        # Stock related
        ('low_stock', 'Low Stock Alert'),
        
        # User related
        ('user_registered', 'New User Registration'),
        ('welcome', 'Welcome Message'),
        
        # Support related
        ('support_ticket', 'New Support Ticket'),
        ('support_replied', 'Support Ticket Reply'),
        ('support_resolved', 'Support Ticket Resolved'),
        
        # Blog related
        ('blog_submitted', 'Blog Post Submitted'),
        ('blog_approved', 'Blog Post Approved'),
        ('blog_rejected', 'Blog Post Rejected'),
        
        # Product related
        ('product_added', 'New Product Added'),
        
        # Marketing
        ('promotional', 'Promotional'),
        ('reminder', 'Reminder'),
        
        # System
        ('system', 'System Notification'),
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Recipients
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(null=True, blank=True, help_text="URL to navigate when notification is clicked")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username if self.recipient else 'No recipient'}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
    
    def get_icon(self):
        """Get FontAwesome icon based on notification type"""
        icons = {
            'order_placed': 'fas fa-shopping-bag',
            'order_confirmed': 'fas fa-check-circle',
            'order_shipped': 'fas fa-truck',
            'order_delivered': 'fas fa-box-open',
            'order_cancelled': 'fas fa-times-circle',
            'order_status': 'fas fa-truck',
            'low_stock': 'fas fa-exclamation-triangle',
            'user_registered': 'fas fa-user-plus',
            'welcome': 'fas fa-hand-wave',
            'support_ticket': 'fas fa-headset',
            'support_replied': 'fas fa-reply',
            'support_resolved': 'fas fa-check-double',
            'blog_submitted': 'fas fa-blog',
            'blog_approved': 'fas fa-thumbs-up',
            'blog_rejected': 'fas fa-edit',
            'product_added': 'fas fa-seedling',
            'promotional': 'fas fa-gift',
            'reminder': 'fas fa-bell',
            'system': 'fas fa-cog',
        }
        return icons.get(self.notification_type, 'fas fa-bell')