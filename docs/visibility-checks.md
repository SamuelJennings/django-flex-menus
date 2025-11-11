# Visibility Checks

Control which users see which menu items using check functions.

## Basic Usage

Pass a `check` parameter to control visibility:

```python
Menu(
    "main_nav",
    children=[
        MenuItem(name="home", view_name="home", check=True),  # Always visible
        MenuItem(name="hidden", view_name="hidden", check=False),  # Never visible
        MenuItem(
            name="admin",
            view_name="admin:index",
            check=lambda request: request.user.is_staff,  # Check function
        ),
    ],
)
```

## Check Function Signature

Check functions receive `request` and optional keyword arguments:

```python
def my_check(request, **kwargs):
    """
    Return True to show item, False to hide.
    
    Args:
        request: Django HttpRequest object
        **kwargs: Additional arguments from process()
    """
    return request.user.is_authenticated
```

## Built-in Checks

Django-flex-menus provides common check functions in `flex_menu.checks`.

### User Status Checks

```python
from flex_menu.checks import (
    user_is_authenticated,
    user_is_anonymous,
    user_is_staff,
    user_is_superuser,
    user_is_active,
)

Menu(
    "main_nav",
    children=[
        MenuItem(name="dashboard", view_name="dashboard", check=user_is_authenticated),
        MenuItem(name="admin", view_name="admin:index", check=user_is_staff),
        MenuItem(name="login", view_name="login", check=user_is_anonymous),
    ],
)
```

### Group Checks

```python
from flex_menu.checks import user_in_any_group, user_in_all_groups

Menu(
    "content_nav",
    children=[
        MenuItem(name="editors", view_name="editors", check=user_in_any_group("editors", "admins")),
        MenuItem(name="super_editors", view_name="super_editors", check=user_in_all_groups("editors", "verified")),
    ],
)
```

### Permission Checks

```python
from flex_menu.checks import has_any_permission, has_all_permissions

Menu(
    "blog_nav",
    children=[
        MenuItem(name="content", view_name="content", check=has_any_permission("blog.add_post", "blog.change_post")),
        MenuItem(name="publish", view_name="publish", check=has_all_permissions("blog.add_post", "blog.publish_post")),
    ],
)
```

### Request Checks

```python
from flex_menu.checks import is_ajax, is_secure, method_is

# Only for AJAX requests
MenuItem(
    name="ajax_menu",
    url="/api/menu/",
    check=is_ajax,
)

# Only for HTTPS
MenuItem(
    name="secure",
    url="/secure/",
    check=is_secure,
)

# Only for specific HTTP methods
MenuItem(
    name="post_only",
    url="/submit/",
    check=method_is("POST"),
)
```

### User Attribute Checks

```python
from flex_menu.checks import user_attribute_equals

# Check custom user attribute
MenuItem(
    name="premium",
    url="/premium/",
    check=user_attribute_equals("is_premium", True),
)
```

## Combining Checks

### AND Logic

All checks must pass:

```python
from flex_menu.checks import combine_checks, user_is_authenticated, user_is_staff

MenuItem(
    name="admin_panel",
    url="/admin/",
    check=combine_checks(
        user_is_authenticated,
        user_is_staff,
        operator="and",
    ),
)
```

### OR Logic

At least one check must pass:

```python
from flex_menu.checks import combine_checks, user_is_staff, user_is_superuser

MenuItem(
    name="moderation",
    url="/moderate/",
    check=combine_checks(
        user_is_staff,
        user_is_superuser,
        operator="or",
    ),
)
```

### NOT Logic

Invert a check:

```python
from flex_menu.checks import negate_check, user_is_staff

# Show to non-staff only
MenuItem(
    name="limited",
    url="/limited/",
    check=negate_check(user_is_staff),
)
```

### Complex Logic

Combine multiple operations:

```python
from flex_menu.checks import (
    combine_checks,
    user_is_authenticated,
    user_in_any_group,
    has_any_permission,
)

# Authenticated AND (in group OR has permission)
check_inner = combine_checks(
    user_in_any_group("premium", "staff"),
    has_any_permission("app.special_access"),
    operator="or",
)

check_final = combine_checks(
    user_is_authenticated,
    check_inner,
    operator="and",
)

MenuItem(
    name="special",
    url="/special/",
    check=check_final,
)
```

## Custom Check Functions

Create your own check functions:

```python
def user_has_profile(request, **kwargs):
    """Show only if user has a complete profile."""
    if not request.user.is_authenticated:
        return False
    return hasattr(request.user, 'profile') and request.user.profile.is_complete

def business_hours(request, **kwargs):
    """Show only during business hours."""
    from datetime import datetime
    hour = datetime.now().hour
    return 9 <= hour < 17

MenuItem(
    name="profile_settings",
    url="/profile/",
    check=user_has_profile,
)

MenuItem(
    name="support",
    url="/support/",
    check=business_hours,
)
```

## Context-Aware Checks

Pass additional context to check functions via template tags. This is useful for checking against database objects or other dynamic data.

**In your menu definition:**

```python
def can_edit_project(request, project=None, **kwargs):
    """Check if user can edit the given project."""
    if not request.user.is_authenticated:
        return False
    if not project:
        return False
    return project.owner == request.user or request.user.is_staff

MenuItem(
    name="project_menu",
    children=[
        MenuItem(name="view", view_name="project_detail"),
        MenuItem(name="edit", view_name="project_edit", check=can_edit_project),
        MenuItem(name="delete", view_name="project_delete", check=can_edit_project),
    ],
)
```

**In your template:**

```django
{% render_menu 'project_menu' renderer='bootstrap5' project=project %}
```

**In your view (alternative):**

```python
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'project.html', {
        'project': project,
    })
```

```django
{# In template - pass project from context #}
{% render_menu 'project_menu' renderer='bootstrap5' project=project %}
```

**Multiple context variables:**

```python
def check_permissions(request, user=None, resource=None, action=None, **kwargs):
    """Generic permission check."""
    if not request.user.is_authenticated:
        return False
    # Your permission logic here
    return has_permission(request.user, resource, action)

MenuItem(
    name="actions",
    children=[
        MenuItem(
            name="edit",
            view_name="edit",
            check=lambda request, **kw: check_permissions(
                request, resource=kw.get('resource'), action='edit', **kw
            ),
        ),
    ],
)
```

```django
{% render_menu 'actions' renderer='simple' resource=document action='edit' %}
```

**Kwargs Usage Summary:**

All keyword arguments passed to `render_menu` or `process_menu` are used in two ways:

1. **Passed to ALL check functions** - Every check function receives all kwargs for context-aware decisions
2. **Filtered for URL resolution** - For `view_name` items, only URL pattern parameters are used; for callable URLs, all kwargs are passed

**URL Parameter Filtering:**

When using `view_name`, django-flex-menus automatically inspects the URL pattern to determine which parameters it needs:

```python
# URL pattern: path('posts/<int:pk>/edit/', views.edit_post, name='post_edit')

MenuItem(name="edit", view_name="post_edit")  # Only uses 'pk' from kwargs
```

```django
{# Pass many kwargs - 'post_edit' only gets 'pk', but check functions get all #}
{% render_menu 'menu' renderer='simple' pk=post.pk user=user project=project %}
```

This filtering means:
- ✅ You can safely pass extra context without breaking URL resolution
- ✅ Check functions always receive full context
- ✅ Failed URL resolution makes items invisible (not errors)
- ✅ Different menu items can need different URL parameters

:::{important}
If you pass kwargs that a `view_name` doesn't expect, `reverse()` will fail and that item becomes **invisible** (not an error). This allows mixing items with different URL requirements in the same menu.
:::

## Parent-Child Visibility

:::{important}
If a parent has no visible children, the parent is automatically hidden.
:::

```python
Menu(
    "main_nav",
    children=[
        MenuItem(
            name="admin",
            children=[
                MenuItem(name="users", view_name="admin:users", check=user_is_staff),
                MenuItem(name="settings", view_name="admin:settings", check=user_is_superuser),
            ],
        ),
    ],
)

# Result:
# - Non-staff: admin section hidden (no visible children)
# - Staff (not super): admin section visible with "users" only
# - Superuser: admin section visible with both children
```

## Debug Check

Show items only in DEBUG mode:

```python
from flex_menu.checks import debug_mode_only

MenuItem(
    name="debug_toolbar",
    url="/debug/",
    check=debug_mode_only,
)
```

## Check Function Reference

### User Status
- `user_is_authenticated(request)` - User logged in
- `user_is_anonymous(request)` - User not logged in
- `user_is_staff(request)` - User has staff status
- `user_is_superuser(request)` - User has superuser status
- `user_is_active(request)` - User account active

### Groups
- `user_in_any_group(*groups)` - User in at least one group
- `user_in_all_groups(*groups)` - User in all groups

### Permissions
- `has_any_permission(*perms)` - User has at least one permission
- `has_all_permissions(*perms)` - User has all permissions

### Request
- `is_ajax(request)` - AJAX request
- `is_secure(request)` - HTTPS request
- `method_is(*methods)` - HTTP method matches

### Attributes
- `user_attribute_equals(attr, value)` - User attribute equals value

### Combinators
- `combine_checks(*checks, operator='and')` - Combine multiple checks
- `negate_check(check)` - Invert check result

### Other
- `debug_mode_only(request)` - Show only when DEBUG=True

## Best Practices

1. **Use built-in checks** - Prefer provided functions over custom lambdas
2. **Test visibility** - Verify menus with different user types
3. **Fail closed** - Return False by default in custom checks
4. **Handle unauthenticated** - Check `request.user.is_authenticated` before accessing user attributes
5. **Parent visibility** - Remember parents hide if all children are hidden
6. **Combine wisely** - Keep complex check logic readable with helper functions
