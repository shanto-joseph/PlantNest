from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import User, Address, PasswordResetToken
from .forms import CustomUserCreationForm, UserProfileForm, AddressForm
from django.urls import reverse

def customer_required(user):
    """Check if user is customer (not admin)"""
    return user.is_authenticated and not user.is_admin

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect based on user role
            if user.is_admin:
                return redirect('admin_control:dashboard')
            else:
                return redirect('product_management:home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create notifications for new user registration
            from apps.admin_control.utils import NotificationService
            from apps.customer_interaction.utils import CustomerNotificationService
            NotificationService.notify_new_user(user)
            CustomerNotificationService.notify_welcome_message(user)
            
            login(request, user)
            messages.success(request, f'Welcome to Plant Store, {user.username}!')
            # Redirect based on user role
            if user.is_admin:
                return redirect('admin_control:dashboard')
            else:
                return redirect('product_management:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('product_management:home')

@user_passes_test(customer_required, login_url='/users/login/')
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_management:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'customer/profile.html', {
        'form': form,
        'addresses': addresses
    })

@user_passes_test(customer_required, login_url='/users/login/')
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('user_management:profile')
    else:
        form = AddressForm()
    
    return render(request, 'customer/add_address.html', {'form': form})

@user_passes_test(customer_required, login_url='/users/login/')
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('user_management:profile')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'customer/edit_address.html', {
        'form': form,
        'address': address
    })

@user_passes_test(customer_required, login_url='/users/login/')
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('user_management:profile')
    
    return render(request, 'customer/delete_address.html', {'address': address})

def forgot_password(request):
    reset_link = None
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        user = None
        if '@' in identifier:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                user = None
        else:
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                user = None
        if user:
            # Create a new reset token
            reset_token = PasswordResetToken.create_token(user)
            reset_link = request.build_absolute_uri(reverse('user_management:reset_password', args=[reset_token.token]))
            print(f"Password reset link for {user.username}: {reset_link}")
            messages.success(request, 'A password reset link has been sent (see terminal).')
        else:
            messages.error(request, 'No user found with that username or email.')
    return render(request, 'auth/forgot_password.html')

def reset_password(request, token):
    reset_token = PasswordResetToken.get_valid_token(token)
    user = reset_token.user if reset_token else None
    
    if request.method == 'POST' and user:
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if not password1 or not password2:
            messages.error(request, 'Please enter both password fields.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        else:
            user.set_password(password1)
            user.save()
            reset_token.mark_as_used()
            messages.success(request, 'Your password has been reset. You can now log in.')
            return redirect('user_management:login')
    
    if not reset_token:
        messages.error(request, 'Invalid or expired reset token.')
        return redirect('user_management:forgot_password')
        
    return render(request, 'auth/reset_password.html', {'token': token, 'user': user})