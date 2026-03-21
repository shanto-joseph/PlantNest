from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import BlogPost, Comment, VideoPost, ChatRoom, ChatMessage
from .forms import CommentForm, CustomerBlogPostForm
from .utils import CustomerNotificationService
from apps.product_management.models import Product
from apps.order_payment.models import Order, OrderItem
import json
from django.utils import timezone

def customer_required(user):
    """Check if user is customer (not admin)"""
    return user.is_authenticated and not user.is_admin

def community_hub(request):
    """Community hub page with videos and blog posts"""
    recent_videos = VideoPost.objects.all()[:6]
    recent_blogs = BlogPost.objects.all()[:6]
    
    context = {
        'recent_videos': recent_videos,
        'recent_blogs': recent_blogs,
    }
    if request.user.is_authenticated:
        context['navbar_notifications'] = CustomerNotificationService.get_user_notifications(request.user, limit=4)
    return render(request, 'customer/community.html', context)

def blog_list(request):
    posts = BlogPost.objects.all()
    category = request.GET.get('category')
    if category:
        posts = posts.filter(category=category)
    
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    # Calculate accurate statistics
    total_posts = BlogPost.objects.count()
    total_categories = BlogPost.objects.values('category').distinct().count()
    total_comments = Comment.objects.filter(is_approved=True).count()
    total_authors = BlogPost.objects.values('author').distinct().count()
    
    context = {
        'posts': posts,
        'total_posts': total_posts,
        'total_categories': total_categories,
        'total_comments': total_comments,
        'total_authors': total_authors,
        'CATEGORY_CHOICES': BlogPost.CATEGORY_CHOICES,
    }
    if request.user.is_authenticated:
        context['navbar_notifications'] = CustomerNotificationService.get_user_notifications(request.user, limit=4)
    return render(request, 'customer/blog.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    comments = post.comments.filter(is_approved=True)
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog_post = post
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('customer_interaction:blog_detail', slug=slug)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    if request.user.is_authenticated:
        context['navbar_notifications'] = CustomerNotificationService.get_user_notifications(request.user, limit=4)
    return render(request, 'customer/blog_detail.html', context)

def video_gallery(request):
    video_posts = VideoPost.objects.all().order_by('-created_at')
    
    paginator = Paginator(video_posts, 9)
    page = request.GET.get('page')
    video_posts = paginator.get_page(page)
    
    context = {
        'video_posts': video_posts,
    }
    if request.user.is_authenticated:
        context['navbar_notifications'] = CustomerNotificationService.get_user_notifications(request.user, limit=4)
    return render(request, 'customer/videos.html', context)

@user_passes_test(customer_required, login_url='/users/login/')
def create_video_post(request):
    if request.method == 'POST':
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_url = request.POST.get('video_url')
        video_file = request.FILES.get('video_file')
        thumbnail = request.FILES.get('thumbnail')
        
        # Ensure at least one video source is provided
        if not video_url and not video_file:
            messages.error(request, 'Please provide either a video URL or upload a video file.')
            return render(request, 'customer/create_video_post.html')
        
        video_post = VideoPost.objects.create(
            title=title,
            description=description,
            video_url=video_url,
            video_file=video_file,
            thumbnail=thumbnail,
            author=request.user,
        )
        
        messages.success(request, 'Your video has been published successfully!')
        return redirect('customer_interaction:my_video_posts')
    
    return render(request, 'customer/create_video_post.html')

@user_passes_test(customer_required, login_url='/users/login/')
def my_video_posts(request):
    videos = VideoPost.objects.filter(author=request.user).order_by('-created_at')
    
    paginator = Paginator(videos, 10)
    page = request.GET.get('page')
    videos = paginator.get_page(page)
    
    return render(request, 'customer/my_video_posts.html', {'videos': videos})


@user_passes_test(customer_required, login_url='/users/login/')
def delete_video_post(request, video_id):
    video = get_object_or_404(VideoPost, id=video_id, author=request.user)
    
    if request.method == 'POST':
        video.delete()
        messages.success(request, 'Video deleted successfully!')
        return redirect('customer_interaction:my_video_posts')
    
    return render(request, 'customer/delete_video_post.html', {'video': video})

@user_passes_test(customer_required, login_url='/users/login/')
def create_blog_post(request):
    if request.method == 'POST':
        form = CustomerBlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            
            messages.success(request, 'Your blog post has been published successfully!')
            return redirect('customer_interaction:my_blog_posts')
    else:
        form = CustomerBlogPostForm()
    
    return render(request, 'customer/create_blog_post.html', {'form': form})

@user_passes_test(customer_required, login_url='/users/login/')
def my_blog_posts(request):
    posts = BlogPost.objects.filter(author=request.user).order_by('-created_at')
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    return render(request, 'customer/my_blog_posts.html', {'posts': posts})


@user_passes_test(customer_required, login_url='/users/login/')
def delete_blog_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted successfully!')
        return redirect('customer_interaction:my_blog_posts')
    
    return render(request, 'customer/delete_blog_post.html', {'post': post})

@user_passes_test(customer_required, login_url='/users/login/')
def customer_notifications(request):
    """View all customer notifications"""
    notifications = CustomerNotificationService.get_user_notifications(request.user)
    
    # Mark notifications as read when viewing notifications page
    unread_notifications = notifications.filter(is_read=False)
    for notification in unread_notifications:
        notification.mark_as_read()
    
    # Pagination
    paginator = Paginator(notifications, 10)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    return render(request, 'customer/notifications.html', {'notifications': notifications})

@user_passes_test(customer_required, login_url='/users/login/')
@require_POST
def mark_customer_notification_read(request, notification_id):
    """Mark a customer notification as read"""
    from apps.admin_control.models import Notification
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@user_passes_test(customer_required, login_url='/users/login/')
@require_POST
def mark_all_customer_notifications_read(request):
    """Mark all customer notifications as read"""
    marked_count = CustomerNotificationService.mark_all_as_read(request.user)
    return JsonResponse({'success': True, 'marked_count': marked_count})

@user_passes_test(customer_required, login_url='/users/login/')
@require_POST
def dismiss_customer_notification(request, notification_id):
    """Dismiss a customer notification"""
    success = CustomerNotificationService.dismiss_notification(notification_id, request.user)
    return JsonResponse({'success': success})

@user_passes_test(customer_required, login_url='/users/login/')
def get_customer_unread_count(request):
    """Get unread notification count for customer"""
    count = CustomerNotificationService.get_unread_count(request.user)
    return JsonResponse({'count': count})

@user_passes_test(customer_required, login_url='/users/login/')
def customer_chat(request):
    """Customer chat interface"""
    # Get or create chat room for customer
    chat_room, created = ChatRoom.objects.get_or_create(
        customer=request.user,
        defaults={'is_active': True}
    )
    
    # Get recent messages
    messages = chat_room.messages.all()[:50]
    
    return render(request, 'customer/chat.html', {
        'chat_room': chat_room,
        'messages': messages
    })

@user_passes_test(customer_required, login_url='/users/login/')
def send_message(request):
    """Send a chat message"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
        
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'})
        
        # Get or create chat room
        chat_room, created = ChatRoom.objects.get_or_create(
            customer=request.user,
            defaults={'is_active': True}
        )
        
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
        print(f"Send Message Error: {str(e)}")  # For debugging
        return JsonResponse({'success': False, 'error': str(e)})

@user_passes_test(customer_required, login_url='/users/login/')
def get_messages(request):
    """Get chat messages for customer"""
    try:
        chat_room = ChatRoom.objects.filter(customer=request.user).first()
        if not chat_room:
            return JsonResponse({'success': True, 'messages': []})
        
        messages = chat_room.messages.all().order_by('created_at')
        
        # Mark messages as read
        unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
        for message in unread_messages:
            message.mark_as_read()
        
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

@user_passes_test(customer_required, login_url='/users/login/')
def mark_messages_read(request):
    """Mark chat messages as read"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
        
    try:
        chat_room = ChatRoom.objects.filter(customer=request.user).first()
        if chat_room:
            unread_messages = chat_room.messages.filter(is_read=False).exclude(sender=request.user)
            for message in unread_messages:
                message.mark_as_read()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})