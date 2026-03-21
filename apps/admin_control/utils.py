from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Notification

User = get_user_model()

class NotificationService:
    """Unified service class for creating and managing all notifications"""
    
    @staticmethod
    def create_notification(title, message, notification_type, recipient=None, action_url=None):
        """Create a new notification"""
        
        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            recipient=recipient,
            action_url=action_url
        )
        
        return notification
    
    # Order notifications
    @staticmethod
    def notify_new_order(order):
        """Create notification for new order (admin)"""
        # Send to all admin users
        admin_users = User.objects.filter(role__name__iexact='admin')
        notifications = []
        for admin_user in admin_users:
            notification = NotificationService.create_notification(
                title="New Order Received",
                message=f"Order #{order.id} from {order.user.username} - ₹{order.total_amount}",
                notification_type="order_placed",
                recipient=admin_user,
                action_url=reverse('admin_control:manage_orders')
            )
            notifications.append(notification)
        return notifications
    
    @staticmethod
    def notify_order_confirmed(order):
        """Create notification for order confirmation (customer)"""
        return NotificationService.create_notification(
            title="New Order Received",
            message=f"Order #{order.id} from {order.user.username} - ₹{order.total_amount}",
            notification_type="order_placed",
            recipient=order.user,
            action_url=reverse('admin_control:manage_orders')
        )
    
    @staticmethod
    def notify_order_shipped(order):
        """Create notification for order shipment (customer)"""
        return NotificationService.create_notification(
            title="Order Shipped!",
            message=f"Great news! Your order #{order.id} has been shipped and is on its way to you.",
            notification_type="order_shipped",
            recipient=order.user,
        )
    
    @staticmethod
    def notify_order_delivered(order):
        """Create notification for order delivery (customer)"""
        return NotificationService.create_notification(
            title="Order Delivered!",
            message=f"Your order #{order.id} has been delivered! We hope you love your new plants.",
            notification_type="order_delivered",
            recipient=order.user,
        )
    
    @staticmethod
    def notify_low_stock(product):
        """Create notification for low stock (admin)"""
        admin_users = User.objects.filter(role__name__iexact='admin')
        notifications = []
        for admin_user in admin_users:
            notification = NotificationService.create_notification(
                title="Low Stock Alert",
                message=f"{product.name} is running low on stock. Only {product.stock_quantity} left.",
                notification_type="low_stock",
                recipient=admin_user,
                action_url=reverse('admin_control:edit_product', args=[product.id])
            )
            notifications.append(notification)
        return notifications
    
    @staticmethod
    def notify_new_user(user):
        """Create notification for new user registration (admin)"""
        admin_users = User.objects.filter(role__name__iexact='admin')
        notifications = []
        for admin_user in admin_users:
            notification = NotificationService.create_notification(
                title="New User Registration",
                message=f"{user.get_full_name() or user.username} ({user.email}) has joined the platform",
                notification_type="user_registered",
                recipient=admin_user,
                action_url=reverse('admin_control:view_user', args=[user.id])
            )
            notifications.append(notification)
        return notifications
    
    @staticmethod
    def notify_welcome_message(user):
        """Create welcome notification for new users (customer)"""
        return NotificationService.create_notification(
            title="Welcome to PlantNest!",
            message="Welcome to our gardening community! Explore our plant collection, read expert tips, and connect with fellow gardeners. Happy gardening!",
            notification_type="welcome",
            recipient=user,
            action_url=reverse('product_management:product_list')
        )
    
    @staticmethod
    def notify_blog_approved(blog_post):
        """Create notification for blog post approval (customer)"""
        return NotificationService.create_notification(
            title="Blog Post Approved!",
            message=f"Congratulations! Your blog post '{blog_post.title}' has been approved and is now live.",
            notification_type="blog_approved",
            recipient=blog_post.author,
            action_url=reverse('customer_interaction:blog_detail', args=[blog_post.slug])
        )
    
    @staticmethod
    def notify_blog_submission(blog_post):
        """Create notification for blog post submission (admin)"""
        admin_users = User.objects.filter(role__name__iexact='admin')
        notifications = []
        for admin_user in admin_users:
            notification = NotificationService.create_notification(
                title="Blog Post Submitted for Review",
                message=f"New blog post '{blog_post.title}' by {blog_post.author.username} needs review",
                notification_type="blog_submitted",
                recipient=admin_user,
                action_url=reverse('admin_control:manage_content')
            )
            notifications.append(notification)
        return notifications
    
    @staticmethod
    def get_user_notifications(user, limit=None, unread_only=False):
        """Get notifications for a specific user"""
        notifications = Notification.objects.filter(recipient=user)
        
        if unread_only:
            notifications = notifications.filter(is_read=False)
        
        if limit:
            notifications = notifications[:limit]
        
        return notifications
    
    @staticmethod
    def get_admin_notifications(user, limit=None, unread_only=False):
        """Get admin notifications for a user"""
        return NotificationService.get_user_notifications(
            user, limit=limit, unread_only=unread_only
        )
    
    @staticmethod
    def get_customer_notifications(user, limit=None, unread_only=False):
        """Get customer notifications for a user"""
        return NotificationService.get_user_notifications(
            user, limit=limit, unread_only=unread_only
        )
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for user"""
        return Notification.objects.filter(
            recipient=user,
            is_read=False
        ).count()
    
    @staticmethod
    def get_admin_unread_count(user):
        """Get count of unread admin notifications"""
        return NotificationService.get_unread_count(user)
    
    @staticmethod
    def get_customer_unread_count(user):
        """Get count of unread customer notifications"""
        return NotificationService.get_unread_count(user)
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for user"""
        notifications = Notification.objects.filter(
            recipient=user,
            is_read=False
        )
        
        count = notifications.count()
        notifications.update(is_read=True)
        return count
    
    @staticmethod
    def dismiss_notification(notification_id, user):
        """Dismiss a notification (delete it)"""
        try:
            notification = Notification.objects.get(id=notification_id, recipient=user)
            notification.delete()
            return True
        except Notification.DoesNotExist:
            return False

    # Simplified notification methods
    @staticmethod
    def notify_order_status_update(order, old_status, new_status):
        """Create notification for order status update"""
        customer_message = f"Your order #{order.order_number} status has been updated to {new_status.title()}"
        return NotificationService.create_notification(
            title="Order Status Updated",
            message=customer_message,
            notification_type="order_status",
            recipient=order.user,
        )