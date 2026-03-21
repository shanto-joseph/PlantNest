from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def is_new_product(created_at, days=7):
    """Check if product was created within the specified number of days"""
    if not created_at:
        return False
    
    now = timezone.now()
    cutoff_date = now - timedelta(days=days)
    return created_at >= cutoff_date

@register.filter
def multiply(value, arg):
    """Multiply two values"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter"""
    if not value:
        return []
    return value.split(delimiter)