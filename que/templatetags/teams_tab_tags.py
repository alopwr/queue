from django import template

register = template.Library()


@register.simple_tag()
@register.filter()
def is_teams(request):
    return "teams" in request.META["HTTP_USER_AGENT"].lower()
