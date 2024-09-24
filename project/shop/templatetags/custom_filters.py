# templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def to_5(value):
    """Generates a range of numbers up to 5."""
    return range(1, 6)
