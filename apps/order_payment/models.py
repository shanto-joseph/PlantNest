from django.db import models
from django.contrib.auth import get_user_model
from apps.product_management.models import Product
from apps.user_management.models import Address
from django.utils import timezone

User = get_user_model()

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    )

    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    )

    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.ForeignKey('user_management.Address', on_delete=models.PROTECT, related_name='orders', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at', 'status']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'total_amount']),
        ]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            import random
            import string
            while True:
                number = ''.join(random.choices(string.digits, k=6))
                order_number = f"ORD-{number}"
                if not Order.objects.filter(order_number=order_number).exists():
                    self.order_number = order_number
                    break
        super().save(*args, **kwargs)
    
    def get_shipping_address_display(self):
        """Return formatted shipping address"""
        if self.shipping_address:
            return self.shipping_address.get_full_address()
        return "No address specified"
    
    def get_payment_status(self):
        """Get payment status from related payment"""
        try:
            return self.payment.is_successful
        except Payment.DoesNotExist:
            return False
    
    def get_payment_method(self):
        """Get payment method from related payment"""
        try:
            return self.payment.get_payment_method_display()
        except Payment.DoesNotExist:
            return "Not specified"
    
    def get_subtotal(self):
        """Calculate subtotal from order items"""
        return sum(item.quantity * item.price for item in self.items.all())

    def get_shipping_cost(self):
        """Get shipping cost (free for now)"""
        return 0

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def get_total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.product.price

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('product_management.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.price

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('card', 'Card Payment'),
        ('razorpay', 'Razorpay'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery')
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment for Order {self.order.order_number}"
    
    @property
    def is_failed(self):
        """Check if payment failed"""
        return not self.is_successful
    
    @property
    def is_refunded(self):
        """Check if payment was refunded (order cancelled after successful payment)"""
        return self.is_successful and self.order.status == 'cancelled'
    
    def get_refund_amount(self):
        """Get refund amount for cancelled orders"""
        if self.is_refunded:
            return self.amount
        return 0