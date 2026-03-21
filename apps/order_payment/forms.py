from django import forms
from django.contrib.auth import get_user_model
from .models import Order, Payment
from apps.user_management.models import Address

User = get_user_model()

class CheckoutForm(forms.Form):
    # Shipping Address Selection
    shipping_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        widget=forms.RadioSelect(attrs={
            'class': 'address-radio'
        }),
        empty_label=None,
        required=True
    )
    
    # Payment Information
    payment_method = forms.ChoiceField(
        choices=[
            ('card', 'Credit/Debit Card'),
            ('razorpay', 'Razorpay (UPI/Netbanking/Cards)')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'payment-method-radio'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user and self.user.is_authenticated:
            # Set user's addresses as choices
            self.fields['shipping_address'].queryset = Address.objects.filter(user=self.user)
            
            # Set default address if available
            default_address = Address.objects.filter(user=self.user, is_default=True).first()
            if default_address:
                self.fields['shipping_address'].initial = default_address

class OrderTrackingForm(forms.Form):
    order_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your order number (e.g., ORD-000001)'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )