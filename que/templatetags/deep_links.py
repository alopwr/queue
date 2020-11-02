from django import template

register = template.Library()


@register.simple_tag()
def chat_deep_link(teacher, student):
    return "https://teams.microsoft.com/l/chat/0/0?users={},{},".format(
        teacher.principal_name, student.principal_name)


@register.filter()
def sub4(queue):
    return len(queue) - 4
