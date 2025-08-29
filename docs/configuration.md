# Configuration

Django Flex Menus provides several configuration options to customize its behavior. These settings can be added to your Django `settings.py` file.

## Settings

### FLEX_MENU_LOG_URL_FAILURES

Controls when URL resolution failures are logged.

**Type**: `bool`  
**Default**: `settings.DEBUG`

When `True`, the system logs warnings when menu URLs can't be resolved (e.g., invalid view names or callable URL functions that raise exceptions). When `False`, URL failures are silently ignored and the menu item is hidden.

**Best practice**: Tie this setting to your `DEBUG` setting so URL issues are logged during development but not in production.

```python
# settings.py

# Recommended approach - log URL failures only in development
FLEX_MENU_LOG_URL_FAILURES = DEBUG

# Alternative configurations:
# FLEX_MENU_LOG_URL_FAILURES = True   # Always log failures
# FLEX_MENU_LOG_URL_FAILURES = False  # Never log failures
```

**Example log output when enabled**:

```log
WARNING:flex_menu.menu: Could not reverse URL for view 'non_existent_view' in menu item 'broken_link'
WARNING:flex_menu.menu: Error calling URL function for menu item 'dynamic_link': 'NoneType' object has no attribute 'id'
```

## Template Configuration


### Required Template Names

Every menu class or instance must have a `template_name` set, either as a class attribute or passed to the constructor. If you do not set `template_name`, a `NotImplementedError` will be raised when rendering the menu.

**Example:**

```python
# Set template_name on an instance
menu = MenuGroup("main_nav", template_name="custom/nav.html")

# Or set a default on a custom class
class CustomMenuGroup(MenuGroup):
    template_name = "custom/menu.html"
```

You are responsible for creating the templates you reference in your Django templates directory.

### Template Directories

Organize your menu templates in a logical structure:

```text
templates/
├── menu/
│   ├── menu.html          # Default MenuGroup template
│   └── item.html          # Default MenuLink/MenuItem template
├── bootstrap5/
│   ├── navbar/
│   │   ├── menu.html
│   │   ├── item.html
│   │   └── dropdown.html
│   └── sidebar/
│       ├── menu.html
│       └── item.html
└── custom/
    ├── admin_menu.html
    └── user_menu.html
```

## Performance Configuration

### URL Caching

Django Flex Menus automatically caches resolved URLs for static menu items (those without dynamic arguments). This caching is built-in and requires no configuration.

**How it works**:

- Static URLs (view names with no args/kwargs) are cached after first resolution
- Failed URL resolutions are also cached to avoid repeated attempts
- Cache is per-menu-instance and persists for the lifetime of the menu object

### Request Processing

Each request gets its own processed copy of menu items to ensure thread safety:

```python
# Original menu definition (shared)
main_nav = MenuGroup("main_navigation")
home = MenuLink("home", view_name="home", parent=main_nav)

# During request processing (creates copies)
processed_menu = main_nav.process(request)  # Thread-safe copy
```

This design ensures that:

- Multiple requests don't interfere with each other
- Menu state (visibility, selection) is request-specific
- Original menu definitions remain unchanged

## Advanced Configuration

### Custom Check Functions

Configure global check functions for common permission patterns:

```python
# utils/menu_checks.py
def requires_login(request, **kwargs):
    """Global check function for authenticated users"""
    return request.user.is_authenticated

def requires_staff(request, **kwargs):
    """Global check function for staff users"""
    return request.user.is_staff

def requires_permission(permission):
    """Factory function for permission-based checks"""
    def check_func(request, **kwargs):
        return request.user.has_perm(permission)
    return check_func

# Usage in menus
user_menu = MenuGroup("user_menu", check=requires_login)
admin_menu = MenuGroup("admin_menu", check=requires_staff)
edit_menu = MenuGroup("edit_menu", check=requires_permission('content.change_article'))
```

### Menu Registration Pattern

Create a centralized menu registration system:

```python
# menus/registry.py
from flex_menu import root

class MenuRegistry:
    def __init__(self):
        self._menus = {}
    
    def register(self, name, menu):
        """Register a menu with a name"""
        self._menus[name] = menu
        menu.parent = root
        return menu
    
    def get(self, name):
        """Get a registered menu by name"""
        return self._menus.get(name)
    
    def all(self):
        """Get all registered menus"""
        return self._menus

# Global registry instance
menu_registry = MenuRegistry()

# menus/main.py
from .registry import menu_registry
from flex_menu.menu import MenuGroup, MenuLink

# Register main navigation
main_nav = MenuGroup("main_navigation")
menu_registry.register("main_nav", main_nav)

# Add items to registered menu
MenuLink("home", view_name="home", parent=main_nav)
MenuLink("about", view_name="about", parent=main_nav)
```

### Environment-Specific Configuration

Configure different behavior for different environments:

```python
# settings/base.py
FLEX_MENU_LOG_URL_FAILURES = True  # Default to logging

# settings/production.py
from .base import *
FLEX_MENU_LOG_URL_FAILURES = False  # Disable logging in production

# settings/development.py
from .base import *
FLEX_MENU_LOG_URL_FAILURES = True   # Enable logging in development

# settings/testing.py
from .base import *
FLEX_MENU_LOG_URL_FAILURES = False  # Disable logging during tests
```

## Management Commands

Django Flex Menus provides management commands for debugging and development.

### render_menu Command

Display the menu tree structure:

```bash
# Show entire menu tree
python manage.py render_menu

# Show specific menu
python manage.py render_menu --name main_navigation
```

**Example output**:

```text
Django Flex Menu:
========================================

DjangoFlexMenu
├── main_navigation
│   ├── home
│   ├── about
│   └── user_menu
│       ├── profile
│       ├── settings
│       └── logout
└── admin_menu
    ├── dashboard
    └── users
```

This command is useful for:

- Debugging menu structure issues
- Verifying menu hierarchy
- Checking that menus are properly registered

## Error Handling

### URL Resolution Failures

When a menu item's URL cannot be resolved:

1. **With logging enabled**: Warning is logged and item is hidden
2. **With logging disabled**: Item is silently hidden
3. **In templates**: Missing URLs result in empty `href` attributes

### Permission Check Failures

When a check function raises an exception:

1. **Development (DEBUG=True)**: Exception is raised
2. **Production (DEBUG=False)**: Item is hidden (fail-safe)

### Template Rendering Failures

When a menu template cannot be found or has errors:

1. **Development**: Django shows the template error
2. **Production**: Depends on your Django error handling configuration

## Integration Patterns

### With Django REST Framework

```python
# For API-driven menus
from rest_framework.permissions import IsAuthenticated

def api_authenticated(request, **kwargs):
    """Check if user is authenticated for API access"""
    return IsAuthenticated().has_permission(request, None)

api_menu = MenuGroup("api_menu", check=api_authenticated)
```

### With Django Guardian (Object Permissions)

```python
from guardian.shortcuts import get_perms

def has_object_permission(permission, obj_key='object'):
    """Check object-level permissions using django-guardian"""
    def check_func(request, **kwargs):
        obj = kwargs.get(obj_key)
        if not obj:
            return False
        return permission in get_perms(request.user, obj)
    return check_func

# Usage
edit_menu = MenuGroup(
    "edit_actions",
    check=has_object_permission('change_article', 'article')
)
```

### With Caching

```python
from django.core.cache import cache

def cached_menu_check(cache_key, timeout=300):
    """Cache check function results"""
    def decorator(check_func):
        def wrapper(request, **kwargs):
            key = f"{cache_key}_{request.user.id}"
            result = cache.get(key)
            if result is None:
                result = check_func(request, **kwargs)
                cache.set(key, result, timeout)
            return result
        return wrapper
    return decorator

@cached_menu_check("user_can_moderate", timeout=600)
def can_moderate(request, **kwargs):
    # Expensive permission check
    return request.user.groups.filter(name="moderators").exists()
```

## Security Considerations

1. **Always validate permissions**: Don't rely solely on menu visibility for security
2. **Use HTTPS**: For production deployments with authentication-based menus
3. **Sanitize user input**: When using dynamic URLs or user-provided data
4. **Follow Django security best practices**: CSRF, XSS prevention, etc.

## Troubleshooting

### Common Issues

1. **Menu items not appearing**: Check URL resolution and permission functions
2. **Template not found**: Verify template paths and INSTALLED_APPS
3. **Performance issues**: Consider caching for expensive check functions
4. **Memory usage**: Large menu trees can consume memory; consider lazy loading

### Debug Steps

1. Enable URL failure logging: `FLEX_MENU_LOG_URL_FAILURES = True`
2. Use the `render_menu` command to check structure
3. Test check functions in Django shell
4. Verify template context in Django debug toolbar

## Next Steps

- Return to [Getting Started](getting-started.md) for basic usage
- See [Simple Menus](simple-menu.md) for static navigation
- Check [Context Aware Menus](context-aware.md) for dynamic content
- Learn about [Templates](templates.md) for customizing appearance 
