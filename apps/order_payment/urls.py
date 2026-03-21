from django.urls import path
from . import views

app_name = 'order_payment'

urlpatterns = [
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/razorpay/', views.razorpay_payment, name='razorpay_payment'),
    path('payment/card/', views.process_card_payment, name='process_card_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('order-history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('track-order/', views.track_order, name='track_order'),
    path('cart-count/', views.get_cart_count, name='cart_count'),
    path('cart-data/', views.get_cart_data, name='cart_data'),
]