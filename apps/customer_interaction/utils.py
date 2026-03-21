from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.admin_control.utils import NotificationService

User = get_user_model()

class CustomerNotificationService:
    """Customer notification service - wrapper around unified NotificationService"""
    
    @staticmethod
    def create_notification(user, title, message, notification_type, action_url=None):
        """Create a new customer notification"""
        return NotificationService.create_notification(
            title=title,
            message=message,
            notification_type=notification_type,
            recipient=user,
            action_url=action_url
        )
    
    @staticmethod
    def notify_order_confirmed(order):
        """Create notification for order confirmation"""
        return NotificationService.notify_order_confirmed(order)
    
    @staticmethod
    def notify_order_shipped(order):
        """Create notification for order shipment"""
        return NotificationService.notify_order_shipped(order)
    
    @staticmethod
    def notify_order_delivered(order):
        """Create notification for order delivery"""
        return NotificationService.notify_order_delivered(order)
    
    @staticmethod
    def notify_order_cancelled(order):
        """Create notification for order cancellation"""
        return NotificationService.create_notification(
            title="Order Cancelled",
            message=f"Your order #{order.order_number} has been cancelled. If you have any questions, please contact our support team.",
            notification_type="order_cancelled",
            recipient=order.user,
            action_url=None
        )
    
    @staticmethod
    def notify_blog_approved(blog_post):
        """Create notification for blog post approval"""
        return NotificationService.notify_blog_approved(blog_post)
    
    @staticmethod
    def notify_blog_rejected(blog_post):
        """Create notification for blog post rejection"""
        return NotificationService.notify_blog_rejected(blog_post)
    
    @staticmethod
    def notify_support_replied(ticket):
        """Create notification for support ticket reply"""
        return NotificationService.notify_support_replied(ticket)
    
    @staticmethod
    def notify_welcome_message(user):
        """Create welcome notification for new users"""
        return NotificationService.notify_welcome_message(user)
    
    @staticmethod
    def get_user_notifications(user, limit=None, unread_only=False):
        """Get notifications for a specific user"""
        return NotificationService.get_customer_notifications(user, limit=limit, unread_only=unread_only)
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for user"""
        return NotificationService.get_customer_unread_count(user)
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for user"""
        return NotificationService.mark_all_as_read(user)
    
    @staticmethod
    def dismiss_notification(notification_id, user):
        """Dismiss a notification"""
        return NotificationService.dismiss_notification(notification_id, user)