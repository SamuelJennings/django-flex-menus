from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from flex_menu import root

register = template.Library()


@register.simple_tag(takes_context=True)
def process_menu(context, menu, **kwargs):
    request = context["request"]
    menu = root.get(menu)
    menu.process(request, **kwargs)
    return menu


@register.simple_tag(takes_context=True)
def render_menu(context, menu, template=None, **kwargs):
    menu = process_menu(context, menu, **kwargs)
    return mark_safe(render_to_string(template or menu.root_template, {"menu": menu}))
