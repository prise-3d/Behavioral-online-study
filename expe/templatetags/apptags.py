# django imports
from django import template

register = template.Library()

@register.filter('from_json')
def get_value_from_json(dict_data, key):
    """
    usage example {{ your_dict| from_json:your_key }}
    """
    
    if key:
        return dict_data.get(key)

@register.filter('duration_minutes')
def duration_minutes(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60 + (hours * 60)

    return '{} min'.format(minutes)

@register.simple_tag
def setvar(val=None):
  return val