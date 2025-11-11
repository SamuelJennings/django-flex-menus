# Manipulating Menus

Django Flex Menus builds on the powerful [anytree](https://anytree.readthedocs.io/) library, which provides a comprehensive set of tools for working with tree structures. This gives you access to a rich API for manipulating menu hierarchies.

## Basic Capabilities from anytree

The anytree library provides fundamental tree operations that work seamlessly with Django Flex Menus:

### Tree Traversal

```python
from anytree import PreOrderIter, PostOrderIter

# Iterate through all nodes in pre-order (parent first, then children)
for item in PreOrderIter(menu):
    print(f"Item: {item.name}, Depth: {item.depth}")

# Iterate through all nodes in post-order (children first, then parent)  
for item in PostOrderIter(menu):
    print(f"Item: {item.name}")
```

### Tree Information

```python
# Get all ancestors of a node
ancestors = item.ancestors

# Get all descendants
descendants = item.descendants  

# Get siblings
siblings = item.siblings

# Check if node is root
is_root = item.is_root

# Check if node is leaf
is_leaf = item.is_leaf

# Get path from root to node
path = item.path
```

## Additional Methods from Django Flex Menus

Django Flex Menus extends anytree with menu-specific functionality:

### Adding Children

```python
parent = MenuItem(name="parent")

# Append
parent.append(MenuItem(name="child1", url="/1/"))

# Extend multiple
parent.extend([
    MenuItem(name="child2", url="/2/"),
    MenuItem(name="child3", url="/3/"),
])
```

### Accessing Children

```python
# Get by name
item = menu.get("child_name")

# Bracket notation
item = menu["child_name"]

# Iterate
for child in menu.children:
    print(child.name)
```

### Insert After

```python
parent.insert_after(
    "existing_child",
    MenuItem(name="new_child", url="/new/"),
)
```

### Remove

```python
# Remove child by name
removed = parent.pop("child_name")

# Remove self from parent
item.pop()
```

## Practical Examples

### Dynamic Menu Building

```python
# Build a menu dynamically based on user permissions
admin_menu = Menu("admin_menu")

if user.has_perm('auth.view_user'):
    admin_menu.append(MenuItem(name="users", view_name="admin:users"))

if user.has_perm('blog.view_post'):
    admin_menu.append(MenuItem(name="posts", view_name="admin:posts"))

# Group related items
if user.is_superuser:
    system_menu = MenuItem(name="system", children=[
        MenuItem(name="settings", view_name="admin:settings"),
        MenuItem(name="logs", view_name="admin:logs"),
    ])
    admin_menu.append(system_menu)
```

### Menu Reorganization

```python
# Find and move items
blog_item = find(main_menu, lambda node: node.name == "blog")
if blog_item:
    # Move blog under a new "content" section
    content_section = MenuItem(name="content")
    main_menu.append(content_section)
    blog_item.parent = content_section
```

### Conditional Menu Items

```python
# Add items based on conditions
for category in user_categories:
    category_item = MenuItem(
        name=f"category_{category.id}",
        view_name="category:detail"
    )
    products_menu.append(category_item)
```

## Further Reading

For more advanced tree operations, consult the [anytree documentation](https://anytree.readthedocs.io/). All anytree features are available when working with Django Flex Menus.