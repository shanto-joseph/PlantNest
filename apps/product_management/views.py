from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Min, Max
from django.db import models
from .models import Product, Category
from apps.order_payment.models import Cart, CartItem, Order, OrderItem

def home(request):
    """Home page view with featured products"""
    featured_products = Product.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()[:4]
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'page_title': 'Welcome to PlantNest'
    }
    return render(request, 'customer/home.html', context)

def product_list(request):
    """Display all active products with filtering"""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    # Get filter parameters
    # Filter by search
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(category__name__icontains=search)
        )
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Filter by eco-friendly
    eco_friendly = request.GET.get('eco_friendly')
    if eco_friendly:
        products = products.filter(is_eco_friendly=True)
    
    # Filter by stock availability
    in_stock = request.GET.get('in_stock')
    if in_stock:
        products = products.filter(stock_quantity__gt=0)
    
    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == '-name':
        products = products.order_by('-name')
    elif sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == '-price':
        products = products.order_by('-price')
    elif sort_by == '-created_at':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-created_at')  # Default sorting
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Get price range for filters
    all_products = Product.objects.filter(is_active=True)
    price_range = all_products.aggregate(
        min_price=models.Min('price'),
        max_price=models.Max('price')
    ) if all_products.exists() else {'min_price': 0, 'max_price': 1000}
    
    context = {
        'products': products,
        'categories': categories,
        'page_title': 'Our Products',
        'price_range': price_range,
        'current_filters': {
            'search': search,
            'category': category_id,
            'min_price': min_price,
            'max_price': max_price,
            'eco_friendly': eco_friendly,
            'in_stock': in_stock,
            'sort': sort_by,
        }
    }
    return render(request, 'customer/products.html', context)

def product_detail(request, product_id):
    """Display product details"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Get related products from same category
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Get recently viewed products (you can implement this with sessions)
    recently_viewed = Product.objects.filter(is_active=True).exclude(id=product.id)[:3]
    
    # Add product to recently viewed (simple implementation)
    if 'recently_viewed' not in request.session:
        request.session['recently_viewed'] = []
    
    recently_viewed_ids = request.session['recently_viewed']
    if product.id not in recently_viewed_ids:
        recently_viewed_ids.insert(0, product.id)
        recently_viewed_ids = recently_viewed_ids[:5]  # Keep only last 5
        request.session['recently_viewed'] = recently_viewed_ids
    
    context = {
        'product': product,
        'related_products': related_products,
        'recently_viewed': recently_viewed,
        'page_title': product.name
    }
    return render(request, 'customer/product_detail.html', context)