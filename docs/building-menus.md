# Building Menus

Complete guide to creating and structuring menus with Menu and MenuItem.

## Menu Class

The `Menu` class is mostly just a convenience wrapper for creating top-level menu containers:

```python
from flex_menu import Menu, MenuItem

# Create a menu - automatically attaches to root
main_nav = Menu(
    "main_nav",
    children=[
        MenuItem(name="home", view_name="home"),
        MenuItem(name="about", view_name="about"),
    ],
)
```

**Menu Parameters:**
- `name` - Required: unique identifier for the menu
- `children` - List of child MenuItems
- `check` - Visibility control (callable or boolean)
- `extra_context` - Additional context for templates

:::{note}
`Menu` provides cleaner syntax for defining top-level menus and automatically handles the parent relationship.
:::

## MenuItem Parameters

```python
MenuItem(
    name="my_item",           # Required: unique identifier
    url="/path/",             # Static URL string
    view_name="app:view",     # Django view name for reverse()
    children=[item1, item2],  # List of child items
    check=callable_or_bool,   # Visibility check function
    extra_context={...},      # Additional template context
)
```

**Required:**
- `name` - Unique identifier for the menu item

**URL options (choose one):**
- `url` - Static URL string or callable returning URL
- `view_name` - Django URL name for `reverse()`

**Optional:**
- `parent` - Parent MenuItem (defaults to `root`)
- `children` - List of child MenuItems
- `check` - Visibility control (callable or boolean)
- `extra_context` - Additional context for templates

## Menu Item Types

### Leaf Nodes

Leaf nodes are menu items that have URLs but no children. They represent actual links that users can click.

#### Static URLs

Direct URL strings:

```python
MenuItem(name="home", url="/")
MenuItem(name="blog", url="/blog/2024/")
MenuItem(name="contact", url="/contact/")
```

#### Django View Names

Use `reverse()` to resolve URLs:

```python
MenuItem(name="profile", view_name="user:profile")
MenuItem(name="settings", view_name="account:settings")
MenuItem(name="about", view_name="about")
```

#### View Names with Arguments

URL parameters should be passed via template tag kwargs, not through `extra_context`. The view will be called only with kwargs necessary for that particular view:

```python
# Menu definition - no URL parameters needed
MenuItem(
    name="category",
    view_name="blog:category",
)

MenuItem(
    name="post",
    view_name="blog:post_detail", 
)
```

Then pass parameters in your template:
```django
{% render_menu "menu_name" category="technology" slug="my-post" %}
```

#### Callable URLs

Dynamically generate URLs at request time. All kwargs passed to the template tag will be passed to the callable:

```python
def get_user_url(request):
    return f"/users/{request.user.id}/"

MenuItem(
    name="my_profile",
    url=get_user_url,
)
```

### Parent Nodes

Parent nodes are menu items that have children but no URL. They create sub-menus that can be rendered as dropdowns, collapsibles, or other navigation structures depending on your renderer.

```python
MenuItem(
    name="products",
    children=[
        MenuItem(name="laptops", view_name="products:category"),
        MenuItem(name="phones", view_name="products:category"),
        MenuItem(name="tablets", view_name="products:category"),
    ],
)

MenuItem(
    name="account", 
    children=[
        MenuItem(name="profile", view_name="user:profile"),
        MenuItem(name="settings", view_name="account:settings"),
        MenuItem(name="logout", view_name="auth:logout"),
    ],
)
```


:::{note}
- Menus can be nested as deep as you like, however, the renderer must be able to handle this.
- You cannot create an item with both a URL and children. This raises `ValueError`.
:::

### Special Nodes

It is easy to create "visual only" node types (for dividers, headings, etc.) by not providing a `url` or `view_name`. However, your render will need to know how to handle these. You can do this via the `get_template` method of the renderer class or in the template itself.

```python
MenuItem(
    name="products",
    children=[
        MenuItem(name="heading_1", extra_context={"heading": True}),
        MenuItem(name="laptops", view_name="products:category"),
        MenuItem(name="divider_1", extra_context={"divider": True}),
        MenuItem(name="accessories", view_name="products:category"),
    ],
)
```

In some cases, it might be more convenient to subclass MenuItem:

```python

class Divider(MenuItem):
    def __init__(self, name):
        super().__init__(name=name, extra_context={"divider": True})

class Heading(MenuItem):
    def __init__(self, name):
        super().__init__(name=name, extra_context={"heading": True})

MenuItem(
    name="products",
    children=[
        Heading(name="divider_1", extra_context={"divider": True}),
        MenuItem(name="laptops", view_name="products:category"),
        Divider(name="divider_1"),
        MenuItem(name="accessories", view_name="products:category"),
    ],
)
```

## Providing Extra Context

The renderer class will pass all the basic context necessary to build your menu templates. However, you can also provide
extra context data on a per-item basis using the `extra_context` parameter.

```python
MenuItem(
    name="special",
    url="/special/",
    extra_context={
        "icon": "star",
        "badge": "New",
        "highlight": True,
    },
)
```

You will now have access to `{{ icon }}`, `{{ badge }}`, and `{{ highlight }}` in your menu templates.

:::{note}
Extra context is merged with the standard context provided by the renderer. This means that you should avoid using keys that the renderer relies on or things may break.
:::
