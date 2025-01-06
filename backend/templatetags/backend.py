from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, None)


@register.filter('startswith')
def startswith(text, start):
    if isinstance(text, str):
        return text.startswith(start)
    return False


@register.filter(name="site_objects")
def site_objects(queryset, request):
    if hasattr(queryset.model, "sites"):
        return queryset.filter(sites=request.site)
    elif hasattr(queryset.model, "site"):
        return queryset.filter(site=request.site)
    else:
        return queryset
