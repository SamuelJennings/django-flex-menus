# Basics

## Menu Classes

Django Flex Menus provides three menu classes which you can use to build your menus: `MenuGroup`, `MenuLink`, and `MenuItem`. Each class serves a different purpose in constructing a menu structure.

:::{note}
These classes are intended to be subclassed in order to create reusable, styled menu components. It's possible to use them directly, but subclassing is strongly recommended for maintainability and consistency.
:::

### MenuLink

A `MenuLink` is the basic building block of a menu and requires either the `view_name` (Django URL name) or `url` parameter. The `url` parameter may be specified as string (e.g. a fully qualified url to an external resource) or a function. For function-based urls and links specified via `view_name`, the URL is resolved at render time. If the url cannot be resolved, the link will be silently hidden. Note: this behavior can be changed in the app configuration (see [Configuration](configuration.md)).

```python
from flex_menu.menu import MenuLink
from flex_menu.checks import user_is_staff

menu_links = [
    MenuLink("home", view_name="home", template_name="menus/link.html"),
    MenuLink("external-link", url="https://example.com", template_name="menus/link.html"),
    MenuLink("dynamic-url", url=resolve_dynamic_url, template_name="menus/link.html"),  # A callable that returns a URL string
]
```

### MenuItem

A non-clickable menu item for decorative elements such as headings or dividers. It does not require a URL or view name.

```python
from flex_menu.menu import MenuItem

divider = MenuItem("divider", template_name="menus/divider.html")
```

### MenuGroup

A `MenuGroup` acts as a container for other menu items. Think of it as a folder or submenu. You can add children to a MenuGroup either at creation time or later via a simple API.

```python
from flex_menu.menu import MenuGroup, MenuLink

# Create a main navigation group with children
main_nav = MenuGroup("main_navigation", 
    template_name="menus/site_navigation.html",  # You must provide a template_name
    children=menu_links, # provide initial children as a list
)

# Add more children later
main_nav.append(MenuLink("contact", view_name="contact"))  

```

## Subclassing Menu Classes

The menu classes above are intended to be subclassed in order to create reusable, consistent and testable menus.

### Specifying a Template

At a bare minumum, you must provide a `template_name` attribute on you subclass. Failing to do so will raise an error at render time.

```python
class BootstrapNavbarLink(MenuLink):
    template_name = "bootstrap/nav_link.html"

class BootstrapNavbar(MenuGroup):
    template_name = "bootstrap/nav_menu.html"
    allowed_children = [BootstrapNavbarLink]
```

### Adding Simple Context Data

Use `extra_context` to pass additional data to templates:

```python

navbar = BootstrapNavbar("main_nav", 
    extra_context={
        "brand": "MySite", 
        "brand_url": "/", 
        "class": "navbar-dark bg-dark"
        },
    children=[
        BootstrapNavbarLink(
            "home", 
            view_name="home", 
            extra_context={"label": "Home", "icon": "fas fa-home"}
            ),
        BootstrapNavbarLink(
            "about", 
            view_name="about", 
            extra_context={"label": "About", "icon": "fas fa-info-circle"}
            ),
    ]
)

```

### Adding Complex Context Data

You can create special subclasses that override `get_context_data()` for dynamic, request-aware context:

```python
class UserAwareLink(MenuLink):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add user-specific data
        if self.request and self.request.user.is_authenticated:
            context.update({
                "user_name": self.request.user.get_full_name(),
                "notification_count": get_user_notifications(self.request.user).count()
            })
        
        return context
```

:::{note}
You are responsible for performance of your application. Ensure that any data fetching in `get_context_data()` is efficient, cached where possible, and does not introduce significant latency.
:::

## Manipulating Menus

Django Flex Menus is built around the `anytree` library which already provides an easy-to-use API for manipulating basic tree
structures. Extra methods are provided by this app which cover common, specific use-cases. Here are some examples:

### Adding Items

```python
# Append to the end
main_nav.append(MenuLink("contact", view_name="contact"))

# Extend with multiple items
new_links = [
    MenuLink("blog", view_name="blog"),
    MenuLink("news", view_name="news")
]
main_nav.extend(new_links)

# Insert at specific position
main_nav.insert(MenuLink("help", view_name="help"), position=1)

# Insert after a named item
main_nav.insert_after(MenuLink("faq", view_name="faq"), named="help")
```

### Finding Items

```python
# Find by name (returns first match)
home_item = main_nav.get("home")

# Access like a dictionary
try:
    about_item = main_nav["about"]
except KeyError:
    print("About menu item not found")

# Search the entire tree
from anytree import search
all_links = search.findall(main_nav, filter_=lambda node: isinstance(node, MenuLink))
```

### Removing Items

```python
# You can easily remove by setting parent to None
home_item.parent = None

# Or pop it from the tree by name
# You can use the returned item if needed
home_item = main_nav.pop("home")
```

## Multi-Level Menus

For complex navigation structures like multi-level dropdowns or tree navigation, you can use the special `"self"` value in the `allowed_children` list. This allows a menu group to contain instances of itself, enabling unlimited nesting.

### Example: Multi-Level Dropdown

```python
from flex_menu.menu import MenuGroup, MenuLink

class MultilevelDropdown(MenuGroup):
    template_name = "menus/multilevel_dropdown.html"
    allowed_children = ["self", MenuLink]  # Allow self-nesting and links

# Create a complex nested structure
main_menu = MultilevelDropdown("main")

# Add regular links
main_menu.append(MenuLink("home", url="/"))

# Create a services submenu
services = MultilevelDropdown("services")
services.append(MenuLink("web_design", url="/services/web/"))

# Create a development sub-submenu
development = MultilevelDropdown("development")
development.append(MenuLink("frontend", url="/services/dev/frontend/"))
development.append(MenuLink("backend", url="/services/dev/backend/"))

# Nest them together
services.append(development)  # development goes into services
main_menu.append(services)    # services goes into main menu
```

This creates a three-level menu structure: Main → Services → Development → Frontend/Backend.

### Self-Reference Types

The `"self"` reference uses exact class matching, not inheritance:

```python
# Allow only self-nesting (strict hierarchy)
class StrictTree(MenuGroup):
    allowed_children = ["self"]

# Mix self-nesting with other types
class FlexibleMenu(MenuGroup):
    allowed_children = ["self", MenuLink, MenuItem]

# Inheritance example
class BaseMenu(MenuGroup):
    allowed_children = ["self"]

class SpecialMenu(BaseMenu):
    pass

base1 = BaseMenu("base1")
base2 = BaseMenu("base2")
special1 = SpecialMenu("special1")

base1.append(base2)      # ✓ Works - exact same class
base1.append(special1)   # ✗ Fails - different class (inheritance doesn't matter for "self")
```

<!-- ### Reordering Items

```python
# Get current children as list
children = list(main_nav.children)

# Reorder as needed
children.reverse()  # Reverse order
children.sort(key=lambda x: x.name)  # Sort alphabetically

# Set new order
main_nav.children = children
``` -->
