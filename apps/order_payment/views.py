from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem, Order, OrderItem, Payment
from .forms import CheckoutForm, OrderTrackingForm
from django.db import transaction
from apps.product_management.models import Product
from apps.user_management.models import Address
import uuid
from decimal import Decimal
import random
import string
import json

def customer_required(user):
    """Check if user is authenticated (allow both customers and admins for testing)"""
    return user.is_authenticated

def get_cart_count(request):
    """Get cart item count for current user"""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.get_total_items()
        except Cart.DoesNotExist:
            count = 0
    else:
        count = 0
    
    return JsonResponse({'count': count})

def get_cart_data(request):
    """Get detailed cart data for mini cart"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        cart = Cart.objects.get(user=request.user)
        items = []
        total = 0
        
        for item in cart.items.all():
            item_data = {
                'id': item.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'quantity': item.quantity,
                'total': float(item.total_price),
                'image': item.product.image.url if item.product.image else None,
                'remove_url': f'/orders/cart/remove/{item.id}/'
            }
            items.append(item_data)
            total += float(item.total_price)
        
        return JsonResponse({
            'success': True,
            'items': items,
            'total': total,
            'count': cart.get_total_items()
        })
        
    except Cart.DoesNotExist:
        return JsonResponse({
            'success': True,
            'items': [],
            'total': 0,
            'count': 0
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@user_passes_test(customer_required, login_url='/users/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get quantity from request
    quantity = 1
    if request.method == 'POST':
        if request.headers.get('Content-Type', '').startswith('application/json'):
            import json
            try:
                data = json.loads(request.body)
                quantity = int(data.get('quantity', 1))
            except Exception:
                quantity = 1
        else:
            quantity = int(request.POST.get('quantity', 1))
    
    # Check stock availability
    if quantity > product.stock_quantity:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Not enough stock available'})
        messages.error(request, f'Only {product.stock_quantity} items available in stock.')
        return redirect('product_management:product_detail', product_id=product_id)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock_quantity:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Not enough stock available'})
            messages.error(request, f'Cannot add more items. Only {product.stock_quantity} available.')
            return redirect('product_management:product_detail', product_id=product_id)
        cart_item.quantity = new_quantity
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('product_management:product_detail', product_id=product_id)

@user_passes_test(customer_required, login_url='/users/login/')
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    context = {
        'cart': cart,
    }
    return render(request, 'customer/cart.html', context)

@user_passes_test(customer_required, login_url='/users/login/')
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            if quantity > cart_item.product.stock_quantity:
                messages.error(request, f'Only {cart_item.product.stock_quantity} items available.')
            else:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated successfully!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
    return redirect('order_payment:view_cart')

@user_passes_test(customer_required, login_url='/users/login/')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('order_payment:view_cart')

@user_passes_test(customer_required, login_url='/users/login/')
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('order_payment:view_cart')
    
    # Check stock availability for all items
    for item in cart.items.all():
        if item.quantity > item.product.stock_quantity:
            messages.error(request, f'{item.product.name} has insufficient stock. Please update your cart.')
            return redirect('order_payment:view_cart')
    
    subtotal = cart.get_total_price()
    shipping_cost = Decimal('0.00')  # Free shipping
    final_total = subtotal + shipping_cost
    
    # Check if user has addresses
    user_addresses = Address.objects.filter(user=request.user)
    if not user_addresses.exists():
        messages.info(request, 'Please add a shipping address before checkout.')
        return redirect('user_management:add_address')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            shipping_address = form.cleaned_data['shipping_address']
            payment_method = form.cleaned_data['payment_method']
            
            # Store order data in session for payment processing
            request.session['checkout_data'] = {
                'shipping_address_id': shipping_address.id,
                'payment_method': payment_method,
                'total_amount': str(final_total),
                'cart_items': [
                    {
                        'product_id': item.product.id,
                        'quantity': item.quantity,
                        'price': str(item.product.price)
                    }
                    for item in cart.items.all()
                ]
            }
            
            if payment_method == 'razorpay':
                return redirect('order_payment:razorpay_payment')
            else:
                # Handle dummy card payment
                return redirect('order_payment:process_card_payment')
    else:
        form = CheckoutForm(user=request.user)
    
    context = {
        'cart': cart,
        'form': form,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'final_total': final_total,
        'user_addresses': user_addresses,
    }
    return render(request, 'customer/checkout.html', context)

@user_passes_test(customer_required, login_url='/users/login/')
def razorpay_payment(request):
    """Handle Razorpay payment"""
    checkout_data = request.session.get('checkout_data')
    if not checkout_data:
        messages.error(request, 'Checkout session expired. Please try again.')
        return redirect('order_payment:checkout')
    
    import razorpay
    
    # Initialize Razorpay client
    client = razorpay.Client(auth=("RAZORPAY_KEY_ID_REMOVED", "RAZORPAY_SECRET_REMOVED"))
    
    amount = int(float(checkout_data['total_amount']) * 100)  # Convert to paise
    
    # Create Razorpay order
    razorpay_order = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': 1
    })
    
    context = {
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': 'RAZORPAY_KEY_ID_REMOVED',
        'amount': amount,
        'currency': 'INR',
        'user': request.user,
        'checkout_data': checkout_data
    }
    
    return render(request, 'customer/razorpay_payment.html', context)

@user_passes_test(customer_required, login_url='/users/login/')
def process_card_payment(request):
    """Handle dummy card payment"""
    checkout_data = request.session.get('checkout_data')
    if not checkout_data:
        messages.error(request, 'Checkout session expired. Please try again.')
        return redirect('order_payment:checkout')
    
    if request.method == 'POST':
        # Simulate card payment processing
        card_number = request.POST.get('card_number', '').replace(' ', '')
        
        # Simple validation for dummy payment
        if len(card_number) >= 16 and card_number.isdigit():
            # Create order after successful payment
            success = create_order_from_session(request, 'card')
            if success:
                return redirect('order_payment:order_success', order_id=success)
            else:
                messages.error(request, 'Failed to create order. Please try again.')
        else:
            messages.error(request, 'Invalid card details. Please try again.')
    
    return render(request, 'customer/card_payment.html', {'checkout_data': checkout_data})

@user_passes_test(customer_required, login_url='/users/login/')
def payment_success(request):
    """Handle payment success callback"""
    if request.method == 'POST':
        # Verify Razorpay payment
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        if razorpay_payment_id and razorpay_order_id:
            # Create order after successful payment
            order_id = create_order_from_session(request, 'razorpay', razorpay_payment_id)
            if order_id:
                return redirect('order_payment:order_success', order_id=order_id)
        
        messages.error(request, 'Payment verification failed.')
        return redirect('order_payment:checkout')
    
    return redirect('order_payment:checkout')

def create_order_from_session(request, payment_method, transaction_id=None):
    """Create order from session data after successful payment"""
    checkout_data = request.session.get('checkout_data')
    if not checkout_data:
        return None
    
    try:
        with transaction.atomic():
            # Get shipping address
            shipping_address = Address.objects.get(
                id=checkout_data['shipping_address_id'],
                user=request.user
            )
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=Decimal(checkout_data['total_amount']),
                shipping_address=shipping_address,
                payment_status='completed',
                status='processing'
            )
            
            # Create order items and update stock
            cart = Cart.objects.get(user=request.user)
            for item_data in checkout_data['cart_items']:
                product = Product.objects.get(id=item_data['product_id'])
                
                # Double-check stock
                if item_data['quantity'] > product.stock_quantity:
                    raise Exception(f'{product.name} has insufficient stock.')
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    price=Decimal(item_data['price'])
                )
                
                # Update product stock
                product.stock_quantity -= item_data['quantity']
                product.save()
            
            # Create payment record
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=Decimal(checkout_data['total_amount']),
                is_successful=True,
                transaction_id=transaction_id or generate_transaction_id()
            )
            
            # Create notifications
            from apps.admin_control.utils import NotificationService
            from apps.customer_interaction.utils import CustomerNotificationService
            NotificationService.notify_new_order(order)
            CustomerNotificationService.notify_order_confirmed(order)
            
            # Clear cart and session
            cart.items.all().delete()
            del request.session['checkout_data']
            
            return order.id
            
    except Exception as e:
        print(f"Error creating order: {e}")
        return None

@user_passes_test(customer_required, login_url='/users/login/')
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get order items with product details
    order_items = order.items.select_related('product').all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'can_review': order.status == 'delivered',
    }
    return render(request, 'customer/order_success.html', context)

def process_payment(order, payment_data):
    """
    Process payment based on payment method
    This is a simplified implementation - in production, integrate with real payment gateways
    """
    payment_method = payment_data['payment_method']
    
    if payment_method == 'cash_on_delivery':
        # COD is always successful
        return True
    elif payment_method in ['credit_card', 'debit_card']:
        # Simulate card payment processing
        # In production, integrate with Stripe, Razorpay, etc.
        card_number = payment_data.get('card_number', '').replace(' ', '')
        
        # Simple validation (in production, use proper payment gateway)
        if len(card_number) >= 13 and card_number.isdigit():
            # Simulate 95% success rate
            return random.random() < 0.95
        return False
    elif payment_method == 'paypal':
        # Simulate PayPal processing
        return random.random() < 0.98
    elif payment_method == 'bank_transfer':
        # Bank transfer requires manual verification
        return True
    
    return False

def generate_transaction_id():
    """Generate a unique transaction ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

@user_passes_test(customer_required, login_url='/users/login/')
def order_history(request):
    """View order history for the customer"""
    orders = Order.objects.filter(user=request.user).select_related('payment').order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
    }
    return render(request, 'customer/order_history.html', context)

@user_passes_test(customer_required, login_url='/users/login/')
def order_detail(request, order_id):
    """View detailed order information"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.select_related('product').all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'can_review': order.status == 'delivered',
    }
    return render(request, 'customer/order_detail.html', context)

def track_order(request):
    """Track order without login"""
    order = None
    form = OrderTrackingForm()
    
    if request.method == 'POST':
        form = OrderTrackingForm(request.POST)
        if form.is_valid():
            order_number = form.cleaned_data['order_number']
            email = form.cleaned_data['email']
            
            try:
                order = Order.objects.get(
                    order_number=order_number,
                    user__email=email
                )
            except Order.DoesNotExist:
                messages.error(request, 'Order not found. Please check your order number and email.')
    
    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'customer/track_order.html', context)

@user_passes_test(customer_required, login_url='/users/login/')
def cancel_order(request, order_id):
    """Cancel an order if it's still pending or processing"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status not in ['pending', 'processing']:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('order_payment:order_detail', order_id=order_id)
    
    if request.method == 'POST':
        with transaction.atomic():
            # Restore stock for cancelled order
            for item in order.items.all():
                item.product.stock_quantity += item.quantity
                item.product.save()
            
            order.status = 'cancelled'
            order.save()
            
            # Create notification
            from apps.customer_interaction.utils import CustomerNotificationService
            CustomerNotificationService.notify_order_cancelled(order)
        
        messages.success(request, f'Order {order.order_number} has been cancelled.')
        return redirect('order_payment:order_history')
    
    context = {'order': order}
    return render(request, 'customer/cancel_order.html', context)