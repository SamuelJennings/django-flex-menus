
# Customizing Menu Templates and Context

Django Flex Menus is designed to let you build menus that look and behave exactly how you want. Instead of forcing you to use a fixed set of templates, it gives you the tools to define your own menu structure, choose your own templates, and provide any context your templates need—static or dynamic.

This guide walks through the three main features you’ll use to control menu rendering: `template_name`, `extra_context`, and `get_context_data`. We’ll use a practical example to show how they work together.

---

## Example: A Custom Sidebar Menu

Suppose you want a sidebar menu with icons, section headings, and links. You want to:

- Use your own HTML templates for each menu part
- Pass extra data (like icons or CSS classes) to your templates
- Optionally provide dynamic context based on the request

Let’s see how you’d do this with Flex Menus.

### 1. Define Your Menu Classes and Templates

Start by subclassing the base menu types and setting a `template_name` for each:

```python
from flex_menu.menu import MenuGroup, MenuLink, MenuItem

class SidebarSection(MenuGroup):
	template_name = "menus/sidebar_section.html"

class SidebarLink(MenuLink):
	template_name = "menus/sidebar_link.html"

class SidebarDivider(MenuItem):
	template_name = "menus/sidebar_divider.html"
```

Now create the templates referenced above. For example, `menus/sidebar_link.html` might look like:

```html
<li class="sidebar-link">
	<a href="{{ url }}">
		<i class="icon {{ icon }}"></i> {{ label }}
	</a>
</li>
```

### 2. Provide Extra Context

When you create menu items, you can pass an `extra_context` dictionary. This lets you inject any variables your template needs:

```python
SidebarLink(
	name="dashboard",
	view_name="dashboard",
	extra_context={"icon": "fa-dashboard", "label": "Dashboard"}
)
```

You can also set `extra_context` as a class attribute if you want all instances to share the same context.

### 3. Use `get_context_data` for Dynamic Context

If you need to add context that depends on the request or other runtime data, override the `get_context_data` method in your menu class:

```python
class UserSection(MenuGroup):
	template_name = "menus/user_section.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if self.request and self.request.user.is_authenticated:
			context["greeting"] = f"Hello, {self.request.user.first_name}!"
		return context
```

Your template can now use `{{ greeting }}` if it’s present.

### 4. What Context Is Available in Templates?

Every menu or menu item template receives:

- `menu`: the menu/item instance itself
- Any variables from `extra_context`
- Any additional context you add in `get_context_data`

For menu groups (like `MenuGroup` subclasses), you also get:

- `children`: the list of visible child menu items
- `has_visible_children`: `True` if any children are visible

### 5. Example: Putting It All Together

Here’s how you might define a sidebar with two sections and a divider:

```python
sidebar = SidebarSection(
	name="main_sidebar",
	extra_context={"section_title": "Main"},
	children=[
		SidebarLink(
			name="dashboard",
			view_name="dashboard",
			extra_context={"icon": "fa-dashboard", "label": "Dashboard"}
		),
		SidebarDivider(name="divider1"),
		SidebarLink(
			name="settings",
			view_name="settings",
			extra_context={"icon": "fa-cog", "label": "Settings"}
		),
	]
)
```

And in your template:

```html
<aside class="sidebar">
	<h2>{{ section_title }}</h2>
	<ul>
		{% for child in children %}
			{{ child.render }}
		{% endfor %}
	</ul>
</aside>
```

---

## Self-Referencing Menus (Multi-Level Nesting)

Sometimes you need menu structures that can nest within themselves, like multi-level dropdown menus or tree-like navigation. Django Flex Menus supports this through the special `"self"` value in the `allowed_children` list.

### Example: Multi-Level Dropdown

```python
class MultilevelDropdown(MenuGroup):
    template_name = "menus/multilevel_dropdown.html"
    allowed_children = ["self", MenuLink, MenuItem]  # Note the "self" reference

# Build a nested structure
main_menu = MultilevelDropdown("main")

# Add regular items
main_menu.append(MenuLink("home", url="/"))

# Add a submenu
services_menu = MultilevelDropdown("services")
services_menu.append(MenuLink("web_design", url="/services/web-design/"))

# Add a sub-submenu (nested within services)
development_menu = MultilevelDropdown("development")
development_menu.append(MenuLink("frontend", url="/services/dev/frontend/"))
development_menu.append(MenuLink("backend", url="/services/dev/backend/"))

services_menu.append(development_menu)  # This works because of "self" in allowed_children
main_menu.append(services_menu)
```

### How Self-References Work

When you include `"self"` in the `allowed_children` list, the menu class allows instances of the **exact same class** to be added as children. This uses exact class matching, not inheritance-based matching.

For example:
```python
class BaseDropdown(MenuGroup):
    allowed_children = ["self"]

class SpecialDropdown(BaseDropdown):
    pass

base1 = BaseDropdown("base1")
base2 = BaseDropdown("base2")
special1 = SpecialDropdown("special1")

base1.append(base2)      # ✓ Works - same class
base1.append(special1)   # ✗ Fails - different class (even with inheritance)
```

This enables:

- Multi-level dropdown menus
- Tree-like navigation structures
- Nested sidebar sections
- Any hierarchical menu pattern

### Combining with Other Types

You can mix `"self"` with other allowed types:

```python
class FlexibleMenu(MenuGroup):
    allowed_children = [MenuLink, MenuItem, "self"]  # Links, dividers, and self-nesting
    
class StrictNesting(MenuGroup):
    allowed_children = ["self"]  # Only allows nesting of the same type
```

---

## Summary

- Use `template_name` to control which template is used for each menu or item.
- Use `extra_context` to pass static or per-instance data to your templates.
- Override `get_context_data` for dynamic, request-aware context.
- All menu templates get the menu instance as `menu`, and menu groups get `children` and `has_visible_children`.

With these tools, you can build menus that are as simple or as sophisticated as your project requires.

