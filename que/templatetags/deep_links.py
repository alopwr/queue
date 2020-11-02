from django import template

register = template.Library()


@register.simple_tag()
def chat_deep_link(teacher, student):
    return "https://teams.microsoft.com/l/chat/0/0?users={},{},".format(
        teacher.principal_name, student.principal_name
    )


@register.filter()
def sub3(queue):
    return len(queue) - 3


@register.filter()
def get3(queue):
    if len(queue) == 4:
        return queue
    return queue[:3]


@register.filter()
def true_length(queue):
    return max(len(queue) - 1, 0)
