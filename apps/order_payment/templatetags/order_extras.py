from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def add_days(value, days):
    """Add days to a date"""
    try:
        if isinstance(value, str):
            # If it's a string, try to parse it as a date
            value = datetime.strptime(value, "%B %d, %Y").date()
        elif hasattr(value, 'date'):
            # If it's a datetime, get the date part
            value = value.date()
        
        # Add the specified number of days
        result = value + timedelta(days=int(days))
        return result.strftime("%B %d, %Y")
    except (ValueError, TypeError, AttributeError):
        return value

@register.filter
def days_until(value):
    """Calculate days until a given date"""
    try:
        if isinstance(value, str):
            value = datetime.strptime(value, "%B %d, %Y").date()
        elif hasattr(value, 'date'):
            value = value.date()
        
        today = datetime.now().date()
        delta = value - today
        return delta.days
    except (ValueError, TypeError, AttributeError):
        return 0