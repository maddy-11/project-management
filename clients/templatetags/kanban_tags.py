from django import template

register = template.Library()

@register.filter
def filter_status(tasks, status_id):
    return [task for task in tasks if task.status_id == status_id]

@register.filter
def endswith(value, arg):
    return str(value).lower().endswith(str(arg).lower())