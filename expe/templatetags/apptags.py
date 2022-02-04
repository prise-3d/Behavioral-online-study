# django imports
from django import template

register = template.Library()

@register.filter('get_value_from_dict')
def get_value_from_dict(dict_data, key):
    """
    usage example {{ your_dict|get_value_from_dict:your_key }}
    """
    
    if key:
        return dict_data.get(key)

@register.filter('duration_minutes')
def duration_minutes(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60 + (hours * 60)

    return '{} min'.format(minutes)