# Simple Example

Django Flex Menus deliberately ships without templates because it is inevitable that you will need to customize the look 
and feel of your menus to suit you site. While you can pass a template_name direct to the constructor of the three basic menu classes, you will be better served by subclassing them and defining your own menu types.

The easiest way to show this is with an example. Let's create a simple Bootstrap 5 navbar menu.

## Example: Bootstrap Navbar

## 1. Create a menus.py module

`django-flex-menus` will automatically discover a `menus.py` module in any of your installed apps and look for menu definitions there. By placing your menu definitions in this module, they will be automatically added to the global "root" menu when your app starts, allowing you to fetch and render them in your templates by name.

```
my_project/
├── manage.py
├── my_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core/
    ├── __init__.py
    ├── apps.py
    ├── menus.py          ← Create this file
    ├── ...
```

## 2. Define your menu classes

We're going to keep this simple and define only two classes to build our menu:

```python
# your_app/menus.py
from flex_menu.menu import MenuGroup, MenuLink

class BootstrapNavLink(MenuLink):
    template_name = "menus/bootstrap_nav_link.html"  # Custom template for links

class BootstrapNavbar(MenuGroup):
    template_name = "menus/bootstrap_navbar.html"     # Custom template for the navbar
    allowed_children = [BootstrapNavLink]              # Only allow nav links as children
```

So, we have defined a `BootstrapNavLink` class that uses a custom template for rendering individual links, and a `BootstrapNavbar` class that uses another custom template for the overall navbar structure. The `allowed_children` attribute ensures that only `BootstrapNavLink` instances can be added as children to the `BootstrapNavbar`. This helps maintain the integrity of our menu structure and prevents accidental misconfiguration.

## 3. Create your templates

Now, we need to create the templates that will define how our menu and links are rendered. You can structure your templates directory as you see fit, but for this example, we'll place them in a `menus` directory within one of your app's template directories.

Let's define a template for the `BootstrapNavbar` first:

```html
<!-- templates/menus/bootstrap_navbar.html -->
<nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
        <a class="navbar-brand" href="#">{{ brand }}</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav">
            {% for child in children %}
                {{ child.render }}
            {% endfor %}
        </ul>
        </div>
    </div>
</nav>
```

As a `MenuGroup` subclass, this template will automatically receive a `children` context variable containing all its child menu items. We loop through these children and call their `render` method to include their HTML. We will also have to pass a `brand` variable via `extra_context` when we instantiate the menu.

Next, let's create the template for the `BootstrapNavLink`:

```html 
<!-- templates/menus/bootstrap_nav_link.html -->
<li class="nav-item">
    <a class="nav-link" href="{{ url }}">{{ label }}</a>
</li>
```

This template renders a single navigation link. It uses the fully resolved `url` context variable provided by the `MenuLink` class. We will have to provide the `label` when we create each link.

## 4. Define your menu instance
Now that we have our menu classes and templates defined, we can create an instance of our `BootstrapNavbar` and populate it with some `BootstrapNavLink` children.

```python
# your_app/menus.py

site_navigation = BootstrapNavbar(
    name="site_navigation", # required for identification within the root menu structure
    extra_context={"brand": "MySite"},        # Pass additional context to the navbar template
    children=[
        BootstrapNavLink(
            name="home",
            view_name="home",                  # Django URL name
            extra_context={"label": "Home"},  # Extra context for the link template
        ),
        BootstrapNavLink(
            name="about",
            view_name="about-us",                     # Static URL
            extra_context={"label": "About Us"},
        ),
        BootstrapNavLink(
            name="contact",
            view_name="contact",
            extra_context={"label": "Contact"},
        )
    ]
)
```

## 5. Render your menu in a template

Finally, you can render your menu in any template by using the `render_menu` template tag provided by `django-flex-menus`. First, ensure you load the `flex_menu_tags` library at the top of your template:

```html
{% load flex_menu %}

{% render_menu "site_navigation" %}
```
