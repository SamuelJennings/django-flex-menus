from django import template

from flex_menu import root

register = template.Library()

@register.simple_tag(takes_context=True)
def process_menu(context, menu, **kwargs):
    request = context["request"]
    if isinstance(menu, str):
        found_menu = root.get(menu)
        if not found_menu:
            raise template.TemplateSyntaxError(
                f"Menu '{menu}' does not exist. "
                "Run 'python manage.py render_menu' to examine the full menu tree."
            )
        menu = found_menu
    if menu:
        # process() now returns a thread-safe copy
        return menu.process(request, **kwargs)
    return None

@register.simple_tag(takes_context=True)
def render_menu(context, menu, **kwargs):
    menu = process_menu(context, menu, **kwargs)
    if not menu:
        return ""

    # Use the menu's render method which handles visibility and context internally
    return menu.render(**kwargs)
