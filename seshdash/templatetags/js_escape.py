"""
For escaping elements in values to be passed to 
javascript 
"""

from django.utils.safestring import mark_safe
from django.template import Library

import json

register = Library()

@register.filter(is_safe=True)
def js_escape(obj):
    return json.dumps(obj)
