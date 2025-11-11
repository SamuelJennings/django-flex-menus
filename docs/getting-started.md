# Getting Started

This guide walks you through installing and setting up django-flex-menus.

## Installation

Install via pip:

```bash
pip install django-flex-menus
```

Add to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    
    # Third-party apps
    'flex_menu',
    
    # Your apps
    'myapp',
]
```

## Configuration

Configure renderers in `settings.py`:

```python
FLEX_MENUS = {
    "renderers": {
        "navbar": "my.custom.NavbarRenderer",
        "mobile_navbar": "my.custom.MobileNavbarRenderer",
        "sidebar": "my.custom.SidebarRenderer",
    },
}
```

:::{note}
Renderers are referenced by name in templates. You can configure as many renderers as needed.
:::

## Create Your First Menu

**1. Create a menu file** (`myapp/menus.py`):

```python
from flex_menu import Menu, MenuItem

# Main navigation
main_nav = Menu(
    "main_nav",
    children=[
        MenuItem(name="home", view_name="home"),
        MenuItem(name="dashboard", view_name="dashboard"),
    ],
)
```

:::{note}
`Menu` is really just a convenience class that automatically attaches to `root`.
:::

**2. Use in templates** (`base.html`):

```django
{% load flex_menu %}

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Site</title>
</head>
<body>
    <nav>
        {% render_menu 'main_nav' renderer='navbar' %}
        <!-- Render the same menu again using a different renderer -->
        {% render_menu 'main_nav' renderer='mobile_navbar' %}
    </nav>
    
    {% block content %}{% endblock %}
</body>
</html>
```

:::{note}
- Menu definitions in `myapp/menus.py` are automatically discovered and loaded by the `flex_menu` app.
- Renderers can declare CSS and JavaScript via a Media subclass which are automatically included when the menu is rendered.
:::

## Menu Structure Basics

Menus are trees with three types of items:

**Leaf**: No children, may or may not have a URL.
```python
# will resolve a URL
MenuItem(name="home", view_name="home")

# Cosmetic only, no URL
MenuItem(name="separator", extra_context={"is_separator": True})
```

**Parent**: Has children, no URL

```python
MenuItem(
    name="products",
    children=[
        MenuItem(name="product_a", view_name="products:detail"),
        MenuItem(name="product_b", view_name="products:detail"),
    ],
)
```

:::{important}
A MenuItem cannot have both a URL and children - it must be one or the other.
:::

## URL Resolution

Three ways to specify URLs:

**1. Static URL string:**
```python
MenuItem(name="home", url="/")
```

**2. Django view name:**
```python
MenuItem(name="about", view_name="about")
MenuItem(name="profile", view_name="user:profile")
```

**3. View name with URL parameters:**
```python
MenuItem(
    name="category",
    view_name="blog:category",
)

MenuItem(
    name="author",
    view_name="blog:author", 
)
```

Then pass the URL parameters in your template:
```django
{% load flex_menu %}
{% render_menu "main" category="tech" slug="john" %}
```

## Next Steps

- [Building Menus](building-menus.md) - Learn all menu features
- [Manipulating Menus](manipulating-menus.md) - Tree operations and dynamic building
- [Template Usage](template-usage.md) - Template tags and rendering
- [Visibility Checks](visibility-checks.md) - Control who sees what
- [Custom Renderers](custom-renderers.md) - Build your own renderer
