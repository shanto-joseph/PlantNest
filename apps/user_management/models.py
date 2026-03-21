from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class PasswordResetToken(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Reset token for {self.user.username}"
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        # Token expires after 24 hours
        expiry_time = self.created_at + timedelta(hours=24)
        return not self.is_used and timezone.now() < expiry_time
    
    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.save()
    
    @classmethod
    def create_token(cls, user):
        """Create a new reset token for user"""
        # Invalidate any existing tokens for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new token
        token = secrets.token_urlsafe(32)
        return cls.objects.create(user=user, token=token)
    
    @classmethod
    def get_valid_token(cls, token):
        """Get a valid token by token string"""
        try:
            reset_token = cls.objects.get(token=token)
            if reset_token.is_valid():
                return reset_token
        except cls.DoesNotExist:
            pass
        return None

class UserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        """Required method for Django's authentication system"""
        return self.get(**{self.model.USERNAME_FIELD: username})
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create and return a superuser with admin role."""
        # Get or create admin role
        admin_role, created = Role.objects.get_or_create(
            name='Admin',
            defaults={'description': 'Administrative access to manage store operations'}
        )
        
        # Set the role for the superuser
        extra_fields['role'] = admin_role
        
        # Create the user
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create and return a regular user with customer role."""
        # Get or create customer role if no role specified
        if 'role' not in extra_fields:
            customer_role, created = Role.objects.get_or_create(
                name='Customer',
                defaults={'description': 'Regular customer with standard shopping permissions'}
            )
            extra_fields['role'] = customer_role
        
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
class User(AbstractUser):
    email = models.EmailField(max_length=191, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, help_text="Tell us about yourself")
    
    # Remove default Django auth fields we don't need
    groups = None
    user_permissions = None
    
    objects = UserManager()
    
    def __str__(self):
        return self.username
    
    def get_profile_picture_url(self):
        """Get profile picture URL with fallback"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return None
    
    def get_display_name(self):
        """Get display name for user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.username
    
    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role and self.role.name.lower() == 'admin'
    
    @property
    def is_customer(self):
        """Check if user has customer role"""
        return self.role and self.role.name.lower() == 'customer'
    
    @property
    def is_staff(self):
        """Property to maintain Django admin compatibility - based on role"""
        return self.is_admin
    
    @property
    def is_superuser(self):
        """Property to maintain Django admin compatibility - based on role"""
        return self.is_admin
    
    def has_perm(self, perm, obj=None):
        """Return True if user has the specified permission"""
        return self.is_admin
    
    def has_perms(self, perm_list, obj=None):
        """Return True if user has each of the specified permissions"""
        return self.is_admin
    
    def has_module_perms(self, app_label):
        """Return True if user has any permissions in the given app"""
        return self.is_admin

class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ('home', 'Home'),
        ('work', 'Work'),
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='home')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address_line = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='india')
    phone_number = models.CharField(max_length=15, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.get_address_type_display()} - {self.first_name} {self.last_name}"
    
    def get_full_address(self):
        """Return formatted full address"""
        address_parts = [
            f"{self.first_name} {self.last_name}",
            self.address_line,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country
        ]
        return '\n'.join(filter(None, address_parts))
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per user per type
        if self.is_default:
            Address.objects.filter(
                user=self.user, 
                address_type=self.address_type, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)