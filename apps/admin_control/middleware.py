from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class AdminAccessControlMiddleware:
    """
    Middleware to prevent admin users from accessing customer-side pages
    and redirect them to appropriate admin pages
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define customer-only URL patterns
        self.customer_only_patterns = [
            'product_management:home',
            'product_management:product_list', 
            'product_management:product_detail',
            'order_payment:view_cart',
            'order_payment:checkout',
            'order_payment:order_success',
            'customer_interaction:blog_list',
            'customer_interaction:blog_detail',
            'customer_interaction:community',
            'customer_interaction:video_gallery',
            'customer_interaction:customer_chat',
            'customer_interaction:customer_notifications',
            'customer_interaction:create_blog_post',
            'customer_interaction:my_blog_posts',
            'customer_interaction:edit_blog_post',
            'customer_interaction:create_video_post',
            'customer_interaction:my_video_posts',
            'customer_interaction:edit_video_post',
            'customer_interaction:delete_video_post',
            'customer_interaction:create_review',
            'customer_interaction:edit_review',
            'customer_interaction:delete_review',
            'customer_interaction:my_reviews',
        ]
        
        # Define admin-only URL patterns
        self.admin_only_patterns = [
            'admin_control:dashboard',
            'admin_control:manage_products',
            'admin_control:add_product',
            'admin_control:edit_product',
            'admin_control:delete_product',
            'admin_control:view_product',
            'admin_control:manage_categories',
            'admin_control:add_category',
            'admin_control:edit_category',
            'admin_control:delete_category',
            'admin_control:manage_orders',
            'admin_control:view_order_details',
            'admin_control:update_order_status',
            'admin_control:manage_users',
            'admin_control:add_user',
            'admin_control:view_user',
            'admin_control:edit_user',
            'admin_control:toggle_user_status',
            'admin_control:delete_user',
            'admin_control:manage_content',
            'admin_control:admin_blog_detail',
            'admin_control:delete_blog_post',
            'admin_control:delete_video_post',
            'admin_control:all_notifications',
            'admin_control:mark_notification_read',
            'admin_control:mark_all_notifications_read',
            'admin_control:dismiss_notification',
            'admin_control:get_unread_count',
            'admin_control:admin_chat',
            'admin_control:admin_chat_room',
            'admin_control:admin_send_message',
            'admin_control:admin_get_messages',
            'admin_control:get_chat_rooms',
            'admin_control:profile',
            'admin_control:analytics',
            'admin_control:api_settings',
            'admin_control:manage_payments',
            'admin_control:view_payment_details',
            'admin_control:process_refund',
        ]
    
    def __call__(self, request):
        # Skip middleware for certain paths
        if self.should_skip_middleware(request):
            return self.get_response(request)
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            current_url_name = self.get_current_url_name(request)
            
            if current_url_name:
                # Admin trying to access customer pages
                if request.user.is_admin and current_url_name in self.customer_only_patterns:
                    messages.warning(request, 'Admin users cannot access customer pages. You have been redirected to the admin panel.')
                    return redirect('admin_control:dashboard')
                
                # Customer trying to access admin pages
                elif not request.user.is_admin and current_url_name in self.admin_only_patterns:
                    messages.error(request, 'You do not have permission to access admin pages.')
                    return redirect('product_management:home')
        
        response = self.get_response(request)
        return response
    
    def should_skip_middleware(self, request):
        """
        Skip middleware for certain paths that should be accessible to all users
        """
        skip_paths = [
            '/admin/',  # Django admin
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
        
        # Skip for authentication URLs
        auth_patterns = [
            'user_management:login',
            'user_management:register', 
            'user_management:logout',
            'user_management:profile',
            'user_management:add_address',
            'user_management:edit_address',
            'user_management:delete_address',
        ]
        
        # Check if path should be skipped
        for skip_path in skip_paths:
            if request.path.startswith(skip_path):
                return True
        
        # Check if it's an auth pattern
        current_url_name = self.get_current_url_name(request)
        if current_url_name in auth_patterns:
            return True
            
        return False
    
    def get_current_url_name(self, request):
        """
        Get the current URL name from the request
        """
        try:
            from django.urls import resolve
            resolved = resolve(request.path)
            if resolved.namespace:
                return f"{resolved.namespace}:{resolved.url_name}"
            return resolved.url_name
        except:
            return None