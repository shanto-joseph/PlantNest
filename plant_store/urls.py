from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.product_management.urls', namespace='product_management')),
    path('users/', include('apps.user_management.urls', namespace='user_management')),
    path('orders/', include('apps.order_payment.urls', namespace='order_payment')),
    path('community/', include('apps.customer_interaction.urls', namespace='customer_interaction')),
    path('admin-panel/', include('apps.admin_control.urls', namespace='admin_control')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)