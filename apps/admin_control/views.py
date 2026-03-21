from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.db import models, transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
import csv

from apps.product_management.models import Product, Category
from apps.user_management.models import User, Role
from apps.order_payment.models import Order, Payment
from apps.customer_interaction.models import BlogPost, Comment, VideoPost, ChatRoom, ChatMessage
from .models import Notification
from .forms import ProductForm, CategoryForm, BlogPostForm, OrderStatusUpdateForm
from .utils import NotificationService
from .api_settings import ApiSettingsForm

def admin_required(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_admin

@user_passes_test(admin_required, login_url='/users/login/')
def admin_dashboard(request):
    """Admin dashboard with overview statistics"""
    # Get basic statistics
    total_products = Product.objects.count()
    total_users = User.objects.filter(role__name__iexact='customer').count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Calculate monthly revenue (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    monthly_revenue = Payment.objects.filter(
        is_successful=True,
        payment_date__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get recent orders and users
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    recent_users = User.objects.filter(role__name__iexact='customer').order_by('-date_joined')[:5]
    
    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'monthly_revenue': monthly_revenue,
        'recent_orders': recent_orders,
        'recent_users': recent_users,
    }
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def manage_products(request):
    """Manage products page"""
    products = Product.objects.select_related('category').order_by('-created_at')
    categories = Category.objects.all()
    
    # Statistics
    total_products = products.count()
    active_products = products.filter(is_active=True).count()
    low_stock_products = products.filter(stock_quantity__lte=5).count()
    eco_products = products.filter(is_eco_friendly=True).count()
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'categories': categories,
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_products': low_stock_products,
        'eco_products': eco_products,
    }
    return render(request, 'admin/manage_products.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def add_product(request):
    """Add new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('admin_control:manage_products')
    else:
        form = ProductForm()
    
    return render(request, 'admin/add_product.html', {'form': form})

@user_passes_test(admin_required, login_url='/users/login/')
def edit_product(request, pk):
    """Edit existing product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('admin_control:manage_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'admin/edit_product.html', {'form': form, 'product': product})

@user_passes_test(admin_required, login_url='/users/login/')
def delete_product(request, pk):
    """Delete product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('admin_control:manage_products')
    
    return render(request, 'admin/delete_product.html', {'product': product})

@user_passes_test(admin_required, login_url='/users/login/')
def view_product(request, pk):
    """View product details"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'admin/view_product.html', {'product': product})

@user_passes_test(admin_required, login_url='/users/login/')
def manage_categories(request):
    """Manage categories page"""
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'admin/manage_categories.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def add_category(request):
    """Add new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" added successfully!')
            return redirect('admin_control:manage_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'admin/add_category.html', {'form': form})

@user_passes_test(admin_required, login_url='/users/login/')
def edit_category(request, pk):
    """Edit existing category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('admin_control:manage_categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'admin/edit_category.html', {'form': form, 'category': category})

@user_passes_test(admin_required, login_url='/users/login/')
def delete_category(request, pk):
    """Delete category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('admin_control:manage_categories')
    
    return render(request, 'admin/delete_category.html', {'category': category})

@user_passes_test(admin_required, login_url='/users/login/')
def manage_orders(request):
    """Manage orders page"""
    orders = Order.objects.select_related('user', 'payment').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 20)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
    }
    return render(request, 'admin/manage_orders.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def view_order_details(request, order_id):
    """View detailed order information"""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.select_related('product').all()
    
    # Calculate totals
    subtotal = sum(item.quantity * item.price for item in order_items)
    shipping_cost = 0  # Free shipping for now
    total_items = sum(item.quantity for item in order_items)
    
    context = {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total_items': total_items,
    }
    return render(request, 'admin/view_order_details.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def update_order_status(request, order_id):
    """Update order status"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.ORDER_STATUS):
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Create notification for status update
            NotificationService.notify_order_status_update(order, old_status, new_status)
            
            messages.success(request, f'Order status updated to {new_status.title()}')
        else:
            messages.error(request, 'Invalid status selected')
    
    return redirect('admin_control:view_order_details', order_id=order_id)

@user_passes_test(admin_required, login_url='/users/login/')
def print_order(request, order_id):
    """Print a single order"""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.select_related('product').all()

    # Calculate totals
    subtotal = sum(item.quantity * item.price for item in order_items)
    shipping_cost = 0  # Free shipping for now
    total_items = sum(item.quantity for item in order_items)

    context = {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total_items': total_items,
    }
    return render(request, 'admin/print_order.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def manage_users(request):
    """Manage users page"""
    users = User.objects.select_related('role').order_by('-date_joined')
    
    # Statistics
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    new_this_month = users.filter(
        date_joined__gte=timezone.now().replace(day=1)
    ).count()
    admin_count = users.filter(role__name__iexact='admin').count()
    
    # Pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'new_this_month': new_this_month,
        'admin_count': admin_count,
    }
    return render(request, 'admin/manage_users.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def add_user(request):
    """Add new user"""
    from apps.user_management.forms import UserProfileForm
    from django import forms
    
    class AdminUserForm(forms.ModelForm):
        password = forms.CharField(widget=forms.PasswordInput, help_text="Enter a password for the user")
        
        class Meta:
            model = User
            fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
            widgets = {
                'username': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control'}),
                'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                'role': forms.Select(attrs={'class': 'form-control'}),
                'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['role'].queryset = Role.objects.all()
            self.fields['is_active'].initial = True
            self.fields['is_active'].help_text = "Designates whether this user can log into the system."
    
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'User "{user.username}" created successfully!')
            return redirect('admin_control:manage_users')
    else:
        form = AdminUserForm()
    
    return render(request, 'admin/add_user.html', {'form': form})

@user_passes_test(admin_required, login_url='/users/login/')
def view_user(request, pk):
    """View user details"""
    user_obj = get_object_or_404(User, pk=pk)
    return render(request, 'admin/view_user.html', {'user_obj': user_obj})

@user_passes_test(admin_required, login_url='/users/login/')
def edit_user(request, pk):
    """Edit user"""
    from django import forms
    
    user_obj = get_object_or_404(User, pk=pk)
    
    class AdminEditUserForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
            widgets = {
                'username': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control'}),
                'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                'role': forms.Select(attrs={'class': 'form-control'}),
                'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['role'].queryset = Role.objects.all()
            self.fields['is_active'].help_text = "Designates whether this user can log into the system."
    
    if request.method == 'POST':
        form = AdminEditUserForm(request.POST, instance=user_obj)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" updated successfully!')
            return redirect('admin_control:view_user', pk=pk)
    else:
        form = AdminEditUserForm(instance=user_obj)
    
    return render(request, 'admin/edit_user.html', {'form': form, 'user_obj': user_obj})

@user_passes_test(admin_required, login_url='/users/login/')
def toggle_user_status(request, pk):
    """Toggle user active status"""
    user_obj = get_object_or_404(User, pk=pk)
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    
    status = "activated" if user_obj.is_active else "deactivated"
    messages.success(request, f'User "{user_obj.username}" {status} successfully!')
    return redirect('admin_control:view_user', pk=pk)

@user_passes_test(admin_required, login_url='/users/login/')
def delete_user(request, pk):
    """Delete user"""
    user_obj = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f'User "{username}" deleted successfully!')
        return redirect('admin_control:manage_users')
    
    return render(request, 'admin/delete_user.html', {'user_obj': user_obj})

@user_passes_test(admin_required, login_url='/users/login/')
def manage_content(request):
    """Enhanced content management page with blogs and videos"""
    # Get basic statistics
    total_blog_posts = BlogPost.objects.count()
    total_video_posts = VideoPost.objects.count()
    total_comments = Comment.objects.count()
    
    # Get recent content for display and management
    recent_blog_posts = BlogPost.objects.select_related('author').order_by('-created_at')[:10]
    recent_video_posts = VideoPost.objects.select_related('author').order_by('-created_at')[:10]
    recent_comments = Comment.objects.select_related('user', 'blog_post').order_by('-created_at')[:10]
    
    if not request.user.is_authenticated:
        # avoid redirecting back to the same page
        return redirect(settings.LOGIN_URL)  # or redirect('account:login') / render login
    if not request.user.is_staff:
        # show a message or raise permission denied instead of redirecting to same view
        messages.error(request, "You do not have permission to access this page.")
        # redirect to admin index or raise PermissionDenied
        return redirect('admin_control:index')  # or: raise PermissionDenied
    
    context = {
        'recent_blog_posts': recent_blog_posts,
        'recent_video_posts': recent_video_posts,
        'recent_comments': recent_comments,
        'total_blog_posts': total_blog_posts,
        'total_video_posts': total_video_posts,
        'total_comments': total_comments,
    }
    return render(request, 'admin/manage_content.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def admin_blog_detail(request, slug):
    """Admin view for blog post details"""
    post = get_object_or_404(BlogPost, slug=slug)
    comments = post.comments.filter(is_approved=True)

    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'admin/blog_detail.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def delete_blog_post(request, blog_id):
    """Delete a blog post"""
    blog_post = get_object_or_404(BlogPost, id=blog_id)

    if request.method == 'POST':
        blog_title = blog_post.title
        blog_post.delete()
        messages.success(request, f'Blog post "{blog_title}" has been deleted successfully.')
        return redirect('admin_control:manage_content')

    return render(request, 'admin/delete_blog_post.html', {'blog_post': blog_post})

@user_passes_test(admin_required, login_url='/users/login/')
def delete_video_post(request, video_id):
    """Delete a video post"""
    video_post = get_object_or_404(VideoPost, id=video_id)
    
    if request.method == 'POST':
        video_title = video_post.title
        video_post.delete()
        messages.success(request, f'Video post "{video_title}" has been deleted successfully.')
        return redirect('admin_control:manage_content')
    
    return render(request, 'admin/delete_video_post.html', {'video_post': video_post})

@user_passes_test(admin_required, login_url='/users/login/')
def all_notifications(request):
    """View all notifications for admin"""
    notifications = NotificationService.get_admin_notifications(request.user)
    
    # Pagination
    paginator = Paginator(notifications, 15)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    return render(request, 'admin/all_notifications.html', {'notifications': notifications})

@user_passes_test(admin_required, login_url='/users/login/')
@require_POST
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@user_passes_test(admin_required, login_url='/users/login/')
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    marked_count = NotificationService.mark_all_as_read(request.user)
    return JsonResponse({'success': True, 'marked_count': marked_count})

@user_passes_test(admin_required, login_url='/users/login/')
@require_POST
def dismiss_notification(request, notification_id):
    """Dismiss notification"""
    success = NotificationService.dismiss_notification(notification_id, request.user)
    return JsonResponse({'success': success})

@user_passes_test(admin_required, login_url='/users/login/')
def get_unread_count(request):
    """Get unread notification count"""
    count = NotificationService.get_admin_unread_count(request.user)
    return JsonResponse({'count': count})

@user_passes_test(admin_required, login_url='/users/login/')
def admin_chat(request):
    """Admin chat dashboard"""
    chat_rooms = ChatRoom.objects.select_related('customer').filter(is_active=True).order_by('-updated_at')
    
    context = {
        'chat_rooms': chat_rooms,
    }
    return render(request, 'admin/chat.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def admin_chat_room(request, room_id):
    """Admin chat room interface"""
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    messages = chat_room.messages.select_related('sender').order_by('created_at')
    
    # Mark messages as read for admin
    unread_messages = messages.filter(is_read=False).exclude(sender__role__name__iexact='admin')
    for message in unread_messages:
        message.mark_as_read()
    
    context = {
        'chat_room': chat_room,
        'messages': messages,
    }
    return render(request, 'admin/chat_room.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
@require_POST
def admin_send_message(request):
    """Send message from admin"""
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'})
        
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        
        # Create message
        message = ChatMessage.objects.create(
            room=chat_room,
            sender=request.user,
            content=content,
            message_type='text'
        )
        
        # Update room timestamp
        chat_room.save()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender': message.sender.username,
                'sender_name': message.sender.get_full_name() or message.sender.username,
                'sender_display_name': message.sender.get_display_name(),
                'sender_profile_picture': message.sender.get_profile_picture_url(),
                'is_admin': message.sender.role.name.lower() == 'admin' if message.sender.role else False,
                'created_at': message.created_at.isoformat(),
                'timestamp': message.created_at.strftime('%H:%M')
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@user_passes_test(admin_required, login_url='/users/login/')
def admin_get_messages(request, room_id):
    """Get messages for admin chat room"""
    try:
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        messages = chat_room.messages.select_related('sender').order_by('created_at')
        
        message_data = []
        for message in messages:
            message_data.append({
                'id': message.id,
                'content': message.content,
                'sender': message.sender.username,
                'sender_name': message.sender.get_full_name() or message.sender.username,
                'sender_display_name': message.sender.get_display_name(),
                'sender_profile_picture': message.sender.get_profile_picture_url(),
                'is_admin': message.sender.role.name.lower() == 'admin' if message.sender.role else False,
                'created_at': message.created_at.isoformat(),
                'timestamp': message.created_at.strftime('%H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'messages': message_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@user_passes_test(admin_required, login_url='/users/login/')
def get_chat_rooms(request):
    """Get chat rooms for admin"""
    try:
        chat_rooms = ChatRoom.objects.select_related('customer').filter(is_active=True).order_by('-updated_at')
        
        rooms_data = []
        for room in chat_rooms:
            last_message = room.get_last_message()
            customer_info = room.get_customer_info()
            rooms_data.append({
                'id': room.id,
                'customer_name': customer_info['display_name'],
                'customer_username': room.customer.username,
                'customer_profile_picture': customer_info['profile_picture'],
                'customer_email': customer_info['email'],
                'last_message': last_message.content[:50] + '...' if last_message and len(last_message.content) > 50 else (last_message.content if last_message else 'No messages yet'),
                'last_message_time': last_message.created_at.isoformat() if last_message else room.created_at.isoformat(),
                'unread_count': room.get_unread_count_for_admin()
            })
        
        return JsonResponse({
            'success': True,
            'rooms': rooms_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@user_passes_test(admin_required, login_url='/users/login/')
def admin_profile(request):
    """Admin profile page"""
    from apps.user_management.forms import UserProfileForm
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('admin_control:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Get statistics for profile
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_customers = User.objects.filter(role__name__iexact='customer').count()
    total_revenue = Payment.objects.filter(is_successful=True).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'form': form,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
    }
    return render(request, 'admin/profile.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def export_analytics(request):
    """Export analytics report as CSV"""
    range_days = int(request.GET.get('range', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=range_days)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analytics_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    
    # General Analytics
    writer.writerow(['Metric', 'Value'])
    current_orders = Order.objects.filter(created_at__gte=start_date).count()
    current_revenue = Payment.objects.filter(is_successful=True, payment_date__gte=start_date).aggregate(total=Sum('amount'))['total'] or 0
    new_customers = User.objects.filter(role__name__iexact='customer', date_joined__gte=start_date).count()
    
    writer.writerow(['Selected Range (days)', range_days])
    writer.writerow(['Total Orders', current_orders])
    writer.writerow(['Total Revenue', f'₹{current_revenue:,.2f}'])
    writer.writerow(['New Customers', new_customers])
    writer.writerow([])

    # Top 5 Products
    writer.writerow(['Top 5 Selling Products'])
    writer.writerow(['Rank', 'Product Name', 'Units Sold', 'Revenue'])
    top_products = Product.objects.filter(orderitem__order__created_at__gte=start_date).annotate(
        total_sold=Sum('orderitem__quantity'),
        total_revenue=Sum(models.F('orderitem__quantity') * models.F('orderitem__price'))
    ).order_by('-total_sold')[:5]

    for i, product in enumerate(top_products, 1):
        writer.writerow([i, product.name, product.total_sold, f'₹{product.total_revenue:,.2f}'])
    writer.writerow([])

    # Sales by Category
    writer.writerow(['Sales by Category'])
    writer.writerow(['Category', 'Total Units Sold', 'Total Revenue'])
    sales_by_category = Category.objects.filter(
        products__orderitem__order__created_at__gte=start_date
    ).annotate(
        total_sales=Sum('products__orderitem__quantity'),
        revenue=Sum(models.F('products__orderitem__quantity') * models.F('products__orderitem__price'))
    ).order_by('-total_sales')

    for category in sales_by_category:
        writer.writerow([category.name, category.total_sales, f'₹{category.revenue:,.2f}'])
    
    return response

@user_passes_test(admin_required, login_url='/users/login/')
def analytics(request):
    """Analytics dashboard"""
    # Get date range from request
    range_days = int(request.GET.get('range', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=range_days)
    
    # Calculate current period metrics
    current_orders = Order.objects.filter(created_at__gte=start_date)
    current_period_orders = current_orders.count()
    current_period_revenue = Payment.objects.filter(
        is_successful=True,
        payment_date__gte=start_date
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate previous period for comparison
    previous_start = start_date - timedelta(days=range_days)
    previous_orders = Order.objects.filter(
        created_at__gte=previous_start,
        created_at__lt=start_date
    )
    previous_period_orders = previous_orders.count()
    previous_period_revenue = Payment.objects.filter(
        is_successful=True,
        payment_date__gte=previous_start,
        payment_date__lt=start_date
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate growth percentages
    def calculate_growth(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100
    
    revenue_growth = calculate_growth(current_period_revenue, previous_period_revenue)
    orders_growth = calculate_growth(current_period_orders, previous_period_orders)
    
    # Calculate average order value
    avg_order_value = current_period_revenue / current_period_orders if current_period_orders > 0 else 0
    previous_avg_order_value = previous_period_revenue / previous_period_orders if previous_period_orders > 0 else 0
    aov_growth = calculate_growth(avg_order_value, previous_avg_order_value)
    
    # New customers
    new_customers = User.objects.filter(
        role__name__iexact='customer',
        date_joined__gte=start_date
    ).count()
    previous_new_customers = User.objects.filter(
        role__name__iexact='customer',
        date_joined__gte=previous_start,
        date_joined__lt=start_date
    ).count()
    customer_growth = calculate_growth(new_customers, previous_new_customers)
    
    # Payment success rate
    total_payments = Payment.objects.filter(payment_date__gte=start_date).count()
    successful_payments = Payment.objects.filter(
        payment_date__gte=start_date,
        is_successful=True
    ).count()
    payment_success_rate = (successful_payments / total_payments * 100) if total_payments > 0 else 0
    
    # Top products
    from django.db.models import Sum as DbSum
    top_products = Product.objects.filter(
        orderitem__order__created_at__gte=start_date
    ).annotate(
        total_sold=DbSum('orderitem__quantity')
    ).order_by('-total_sold')[:5]
    
    # Sales by category
    sales_by_category = Category.objects.filter(
        products__orderitem__order__created_at__gte=start_date
    ).annotate(
        total_sales=DbSum('products__orderitem__quantity'),
        revenue=DbSum('products__orderitem__price')
    ).order_by('-total_sales')
    
    # Customer metrics
    customer_metrics = {
        'repeat_rate': 75.5,  # Placeholder
        'avg_satisfaction': 4.2,  # Placeholder
        'avg_reviews': 3.8,  # Placeholder
    }
    
    # Payment methods breakdown
    payment_methods_breakdown = [
        {'method_display': 'Razorpay', 'count': 45, 'percentage': 60.0},
        {'method_display': 'Card Payment', 'count': 25, 'percentage': 33.3},
        {'method_display': 'Cash on Delivery', 'count': 5, 'percentage': 6.7},
    ]
    
    # Revenue and orders data for charts (simplified)
    revenue_data = []
    orders_data = []
    for i in range(range_days):
        date = start_date + timedelta(days=i)
        daily_revenue = Payment.objects.filter(
            is_successful=True,
            payment_date__date=date.date()
        ).aggregate(total=Sum('amount'))['total'] or 0
        daily_orders = Order.objects.filter(
            created_at__date=date.date()
        ).count()
        
        revenue_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'total': float(daily_revenue)
        })
        orders_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': daily_orders
        })
    
    # Payment statistics
    payment_stats = {
        'successful_payments': successful_payments,
        'failed_payments': total_payments - successful_payments,
        'refunded_payments': 0,  # Placeholder
        'pending_payments': 0,  # Placeholder
    }
    
    # Recent payments with enhanced data
    recent_payments = []
    payments = Payment.objects.select_related('order__user').filter(
        payment_date__gte=start_date
    ).order_by('-payment_date')[:10]
    
    for payment in payments:
        recent_payments.append({
            'payment': payment,
            'is_refunded': payment.order.status == 'cancelled' and payment.is_successful,
            'refund_amount': payment.amount if payment.order.status == 'cancelled' and payment.is_successful else 0
        })
    
    context = {
        'selected_range': range_days,
        'current_period_revenue': current_period_revenue,
        'current_period_orders': current_period_orders,
        'revenue_growth': revenue_growth,
        'orders_growth': orders_growth,
        'avg_order_value': avg_order_value,
        'aov_growth': aov_growth,
        'new_customers': new_customers,
        'customer_growth': customer_growth,
        'payment_success_rate': payment_success_rate,
        'top_products': top_products,
        'sales_by_category': sales_by_category,
        'customer_metrics': customer_metrics,
        'payment_methods_breakdown': payment_methods_breakdown,
        'revenue_data': json.dumps(revenue_data),
        'orders_data': json.dumps(orders_data),
        'payment_stats': payment_stats,
        'recent_payments': recent_payments,
    }
    return render(request, 'admin/analytics.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def api_settings(request):
    """API Settings page"""
    import os
    
    if request.method == 'POST':
        form = ApiSettingsForm(request.POST)
        if form.is_valid():
            google_ai_api_key = form.cleaned_data['google_ai_api_key']
            
            # Update environment variable (this is a simplified approach)
            # In production, you'd want to store this in a secure configuration system
            if google_ai_api_key:
                os.environ['GOOGLE_AI_API_KEY'] = google_ai_api_key
                messages.success(request, 'Google AI API Key updated successfully!')
            else:
                messages.info(request, 'No changes made to API settings.')
            
            return redirect('admin_control:api_settings')
    else:
        # Pre-populate form with current values
        current_key = os.getenv('GOOGLE_AI_API_KEY', '')
        # Mask the key for security (show only first 8 and last 4 characters)
        if current_key and len(current_key) > 12:
            masked_key = current_key[:8] + '*' * (len(current_key) - 12) + current_key[-4:]
        else:
            masked_key = current_key
        
        form = ApiSettingsForm(initial={'google_ai_api_key': masked_key})
    
    return render(request, 'admin/api_settings.html', {'form': form})

@user_passes_test(admin_required, login_url='/users/login/')
def manage_payments(request):
    """Manage payments page"""
    payments = Payment.objects.select_related('order__user').order_by('-payment_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'successful':
        payments = payments.filter(is_successful=True)
    elif status_filter == 'failed':
        payments = payments.filter(is_successful=False)
    
    # Filter by payment method
    method_filter = request.GET.get('method')
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    # Filter by date range
    date_filter = request.GET.get('date_range')
    if date_filter:
        if date_filter == 'today':
            payments = payments.filter(payment_date__date=timezone.now().date())
        elif date_filter == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            payments = payments.filter(payment_date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            payments = payments.filter(payment_date__gte=month_ago)
    
    # Calculate statistics
    total_payments = payments.count()
    successful_payments = payments.filter(is_successful=True).count()
    failed_payments = payments.filter(is_successful=False).count()
    total_amount = payments.filter(is_successful=True).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Payment method breakdown
    payment_methods = payments.values('payment_method').annotate(
        count=Count('id'),
        total_amount=Sum('amount', filter=models.Q(is_successful=True))
    ).order_by('-count')
    
    # Recent failed payments for attention
    recent_failed = payments.filter(
        is_successful=False,
        payment_date__gte=timezone.now() - timedelta(days=7)
    )[:5]
    
    # Pagination
    paginator = Paginator(payments, 20)
    page = request.GET.get('page')
    payments = paginator.get_page(page)
    
    context = {
        'payments': payments,
        'total_payments': total_payments,
        'successful_payments': successful_payments,
        'failed_payments': failed_payments,
        'total_amount': total_amount,
        'payment_methods': payment_methods,
        'recent_failed': recent_failed,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'date_filter': date_filter,
    }
    return render(request, 'admin/manage_payments.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
def view_payment_details(request, payment_id):
    """View detailed payment information"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Get related order items
    order_items = payment.order.items.select_related('product').all()
    
    # Calculate refund information
    is_refundable = (
        payment.is_successful and 
        payment.order.status in ['pending', 'processing', 'cancelled'] and
        not payment.is_refunded
    )
    
    context = {
        'payment': payment,
        'order_items': order_items,
        'is_refundable': is_refundable,
    }
    return render(request, 'admin/view_payment_details.html', context)

@user_passes_test(admin_required, login_url='/users/login/')
@require_POST
def process_refund(request, payment_id):
    """Process a payment refund"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if not payment.is_successful:
        messages.error(request, 'Cannot refund a failed payment.')
        return redirect('admin_control:view_payment_details', payment_id=payment_id)
    
    if payment.is_refunded:
        messages.error(request, 'This payment has already been refunded.')
        return redirect('admin_control:view_payment_details', payment_id=payment_id)
    
    try:
        with transaction.atomic():
            # Update order status to cancelled
            payment.order.status = 'cancelled'
            payment.order.save()
            
            # Restore stock for cancelled order
            for item in payment.order.items.all():
                item.product.stock_quantity += item.quantity
                item.product.save()
            
            # Create notification for customer
            NotificationService.create_notification(
                title="Refund Processed",
                message=f"Your refund of ₹{payment.amount} for order #{payment.order.order_number} has been processed and will be credited to your account within 5-7 business days.",
                notification_type="order_cancelled",
                recipient=payment.order.user,
            )
            
            messages.success(request, f'Refund of ₹{payment.amount} has been processed successfully.')
            
    except Exception as e:
        messages.error(request, f'Error processing refund: {str(e)}')

    return redirect('admin_control:view_payment_details', payment_id=payment_id)

@user_passes_test(admin_required, login_url='/users/login/')
def export_revenue_report(request):
    """Export revenue report as CSV"""
    range_days = int(request.GET.get('range', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=range_days)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="revenue_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Order Number', 'Customer', 'Amount', 'Payment Method', 'Status'])

    payments = Payment.objects.select_related('order__user').filter(
        payment_date__gte=start_date,
        is_successful=True
    ).order_by('-payment_date')

    for payment in payments:
        writer.writerow([
            payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
            payment.order.order_number,
            payment.order.user.get_full_name() or payment.order.user.username,
            f'₹{payment.amount}',
            payment.get_payment_method_display(),
            'Success' if payment.is_successful else 'Failed'
        ])

    return response

@user_passes_test(admin_required, login_url='/users/login/')
def export_orders_report(request):
    """Export orders report as CSV"""
    range_days = int(request.GET.get('range', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=range_days)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="orders_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order Number', 'Customer', 'Email', 'Date', 'Status', 'Items', 'Total Amount', 'Payment Status'])

    orders = Order.objects.select_related('user', 'payment').prefetch_related('items').filter(
        created_at__gte=start_date
    ).order_by('-created_at')

    for order in orders:
        items_count = order.items.count()
        total_amount = sum(item.quantity * item.price for item in order.items.all())
        payment_status = 'Paid' if hasattr(order, 'payment') and order.payment.is_successful else 'Unpaid'

        writer.writerow([
            order.order_number,
            order.user.get_full_name() or order.user.username,
            order.user.email,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            order.get_status_display(),
            items_count,
            f'₹{total_amount}',
            payment_status
        ])

    return response

@user_passes_test(admin_required, login_url='/users/login/')
def export_customers_report(request):
    """Export customers report as CSV"""
    range_days = int(request.GET.get('range', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=range_days)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="customers_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Full Name', 'Email', 'Phone', 'Date Joined', 'Total Orders', 'Total Spent', 'Status'])

    customers = User.objects.filter(role__name__iexact='customer')

    for customer in customers:
        orders_count = Order.objects.filter(user=customer, created_at__gte=start_date).count()
        total_spent = Payment.objects.filter(
            order__user=customer,
            is_successful=True,
            payment_date__gte=start_date
        ).aggregate(total=Sum('amount'))['total'] or 0

        writer.writerow([
            customer.username,
            customer.get_full_name() or 'N/A',
            customer.email,
            customer.phone_number or 'N/A',
            customer.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            orders_count,
            f'₹{total_spent}',
            'Active' if customer.is_active else 'Inactive'
        ])

    return response

@user_passes_test(admin_required, login_url='/users/login/')
def export_products_report(request):
    """Export products report as CSV"""
    range_days = int(request.GET.get('range', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=range_days)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="products_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Product Name', 'Category', 'Price', 'Stock', 'Units Sold', 'Revenue', 'Status'])

    products = Product.objects.select_related('category').all()

    for product in products:
        units_sold = product.orderitem_set.filter(
            order__created_at__gte=start_date
        ).aggregate(total=Sum('quantity'))['total'] or 0

        revenue = product.orderitem_set.filter(
            order__created_at__gte=start_date,
            order__payment__is_successful=True
        ).aggregate(total=Sum(models.F('quantity') * models.F('price')))['total'] or 0

        writer.writerow([
            product.name,
            product.category.name if product.category else 'N/A',
            f'₹{product.price}',
            product.stock_quantity,
            units_sold,
            f'₹{revenue}',
            'Active' if product.is_active else 'Inactive'
        ])

    return response