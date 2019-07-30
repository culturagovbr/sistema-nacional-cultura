from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, field, value):
    request = context['request']

    dict = request.GET.copy()

    dict[field] = value

    return dict.urlencode()

@register.filter(name='has_group')
def has_group(user, group_name):
    if user:
        return not user.groups.filter(name=group_name).count() == 0
    return True
