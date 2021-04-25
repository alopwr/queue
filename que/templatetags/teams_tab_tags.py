from django import template

register = template.Library()


@register.simple_tag()
@register.filter()
def is_teams(request):
    try:
        return "teams" in request.META.get("HTTP_USER_AGENT").lower()
    except AttributeError:
        return False
