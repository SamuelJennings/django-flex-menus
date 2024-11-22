# Django Flex Menu

A flexible menu management system for Django built around [anytree](https://github.com/c0fec0de/anytree).


## Features

- Modular, tree-based design for easy customization and extension
- Flexible URL resolution 
- Object-based processing for detail view menus

## Installation


## API

Once you have a menu instance, you can modify it in the following ways:

```python

main_menu = Menu("Site Menu")
child_menu = MenuItem("My Child", url="/my-child")

# Append a child 
main_menu.append(child_menu)

# Get a child instance by name
child_menu = main_menu.get("My Child")

# Pop a child (note this is done via the child menu, not the parent menu)
child = child_menu.pop()

# Extend a menu with a list of menu items
main_menu.extend([child_menu, child_menu2, child_menu3])

# Insert child/children at a specific position
main_menu.insert(child_menu, 2)

# Insert child after another named child
main_menu.insert_after(child_menu, "My Other Child")






## See also

[django-account-management](https://github.com/SamuelJennings/django-account-management)