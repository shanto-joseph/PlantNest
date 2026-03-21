from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.product_management.models import Product
from apps.order_payment.models import Order

User = get_user_model()

class ChatRoom(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_chat_rooms')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat with {self.customer.username}"
    
    def get_last_message(self):
        return self.messages.last()
    
    def get_customer_info(self):
        """Get customer information for chat display"""
        return {
            'username': self.customer.username,
            'display_name': self.customer.get_display_name(),
            'profile_picture': self.customer.get_profile_picture_url(),
            'email': self.customer.email
        }
    
    def get_unread_count(self):
        """Get count of unread messages in this room"""
        return self.messages.filter(is_read=False).exclude(sender__is_admin=True).count()
    
    def get_unread_count_for_admin(self):
        """Get count of unread messages for admin (from customers)"""
        return self.messages.filter(is_read=False).exclude(sender__role__name__iexact='admin').count()

class ChatMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    )
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.room}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

class BlogPost(models.Model):
    CATEGORY_CHOICES = (
        ('tips', 'Gardening Tips'),
        ('diy', 'DIY Projects'),
        ('sustainability', 'Sustainability'),
        ('plant_care', 'Plant Care'),
        ('seasonal', 'Seasonal Gardening'),
        ('community', 'Community Stories'),
        ('experience', 'My Experience'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(self.title)
            # Create a shorter, more manageable slug
            if len(base_slug) > 80:
                base_slug = base_slug[:80]
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
            
        super().save(*args, **kwargs)

class Comment(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog_post.title}"

class VideoPost(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True)  # For YouTube/Vimeo links
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title