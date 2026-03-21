from django.urls import path
from . import views
from . import plant_ai_view

app_name = 'customer_interaction'

urlpatterns = [
    path('plant-ai-chat/', plant_ai_view.plant_ai_chat, name='plant_ai_chat'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('community/', views.community_hub, name='community'),
    path('create/', views.create_blog_post, name='create_blog_post'),
    path('my-posts/', views.my_blog_posts, name='my_blog_posts'),
    path('my-posts/delete/<slug:slug>/', views.delete_blog_post, name='delete_blog_post'),
    path('videos/', views.video_gallery, name='video_gallery'),
    path('videos/create/', views.create_video_post, name='create_video_post'),
    path('videos/my/', views.my_video_posts, name='my_video_posts'),
    path('videos/delete/<int:video_id>/', views.delete_video_post, name='delete_video_post'),
    path('chat/', views.customer_chat, name='customer_chat'),
    path('chat/api/send/', views.send_message, name='send_message'),
    path('chat/api/messages/', views.get_messages, name='get_messages'),
    path('chat/api/mark-read/', views.mark_messages_read, name='mark_messages_read'),
    path('notifications/', views.customer_notifications, name='customer_notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_customer_notification_read, name='mark_customer_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_customer_notifications_read, name='mark_all_customer_notifications_read'),
    path('notifications/dismiss/<int:notification_id>/', views.dismiss_customer_notification, name='dismiss_customer_notification'),
    path('notifications/api/unread-count/', views.get_customer_unread_count, name='get_customer_unread_count'),
]