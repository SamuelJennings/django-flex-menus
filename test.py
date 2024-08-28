from anytree import Node, RenderTree
from anytree.search import find


class MenuItem(Node):
    template = "menu/menu_link.html"


    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def __str__(self):
        return f"MenuItem(name={self.name})"

    @property
    def visible(self):
        return True

class Menu(Node):
    template = "menu/menu.html"
    
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def __str__(self):
        return self.render()

    def __getitem__(self, name: str):
        node = self.get(name)
        if node is None:
            raise KeyError(f"No child with name {name} found.")
        return node

    def __iter__(self):
        for child in self.children:
            yield child

    def append(self, child):
        child.parent = self

    def insert_before(self, child, named: str):
        existing_child = self.get(named)
        if existing_child:
            child.parent = self
            child._move_before(existing_child)
        else:
            raise ValueError(f"No child with name {named} found.")

    def insert_after(self, child, named: str):
        if isinstance(child, Menu) or isinstance(child, MenuItem):
            existing_child = self.get(named)
            if existing_child:
                child.parent = self
                child._move_after(existing_child)
            else:
                raise ValueError(f"No child with name {named} found.")
        else:
            raise TypeError("Child must be an instance of Menu or MenuItem.")

    def pop(self):
        self.parent = None  # Removes the node from the tree
        return self

    def get(self, name: str):
        return find(self, lambda node: node.name == name)

    def render(self):
        return RenderTree(self).by_attr("name")

    @property
    def visible(self):
        return any([child.visible for child in self.children])

# Example Usage:
main_menu = Menu("MainMenu", children=[
    Menu("File", children=[
        MenuItem("New"),
        MenuItem("Open"),
        MenuItem("Save"),
        MenuItem("Save As"),
        MenuItem("Exit"),
    ]),
    Menu("Edit", children=[
        MenuItem("Undo"),
        MenuItem("Redo"),
        MenuItem("Cut"),
        MenuItem("Copy"),
        MenuItem("Paste"),
    ]),
    Menu("Help", children=[
        MenuItem("About"),
        MenuItem("Documentation"),
        MenuItem("Report Issue"),
    ]),
    Menu("Logout"),
])



def iter_children(node):
    for child in node:
        if child.children:
            print(child.name, "is submenu.")
            iter_children(child.children)
        else:
            print(child.name, "is a link.")

iter_children(main_menu)

file = main_menu["File"].pop()

print(main_menu)

main_menu.append(file)

# print(file)


# for item in PreOrderIter(main_menu):
#     if item.is_leaf:
#         print(item.name, "is a leaf node.")

