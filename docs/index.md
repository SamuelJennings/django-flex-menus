# Django Flex Menus

A flexible, hierarchical menu system for Django applications that supports dynamic visibility, URL resolution, and request-aware processing.

## Features

- **Hierarchical Menu Structure**: Build complex nested menus with ease
- **Dynamic Visibility**: Menu items can show/hide based on user permissions, request context, or custom logic
- **Object-Specific Menus**: Create context-aware menus for object detail pages with user-tailored permissions
- **Thread-Safe Processing**: Each request gets its own processed copy to prevent race conditions
- **URL Resolution**: Support for Django view names, static URLs, and callable URL functions
- **Template Integration**: Simple template tags for rendering menus
- **Extensible**: Easy to extend with custom menu types and behaviors

## Quick Start

### Installation

```bash
pip install django-flex-menus
```

### Add to Django Settings

```python
INSTALLED_APPS = [
    # ... your other apps
    'flex_menu',
]
```

## Documentation Contents

```{toctree}
:maxdepth: 2

getting-started
simple-example
templates
context-aware-example
dynamic-url-resolution
checks
configuration
```

## License

MIT License - see LICENSE file for details.