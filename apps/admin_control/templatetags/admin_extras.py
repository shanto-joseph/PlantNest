from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def days_since(value):
    if not value:
        return ""
    now = timezone.now()
    delta = now - value
    return delta.days 