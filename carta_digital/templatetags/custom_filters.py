# carta_digital/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def startswith(value, arg):
    """Checks if a string starts with the given argument."""
    return value.startswith(arg)