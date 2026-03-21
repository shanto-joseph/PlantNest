from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_active', 'is_eco_friendly', 'created_at')
    list_filter = ('category', 'is_active', 'is_eco_friendly', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock_quantity', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'price', 'stock_quantity')
        }),
        ('Product Details', {
            'fields': ('image', 'is_active', 'is_eco_friendly')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )