from django import template

register = template.Library()


@register.filter
def Sexy_capitals(value):
    print("value")
    return "asdfasdfsef"
