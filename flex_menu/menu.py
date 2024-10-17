import re
from contextlib import suppress

from anytree import Node, RenderTree, search
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch


class BaseMenu(Node):
    def __init__(
        self,
        name: str,
        parent=None,
        children=None,
        check=None,
        resolve_url=None,
        **kwargs,
    ):
        super().__init__(name, parent=parent, children=children, **kwargs)
        self.label = kwargs.get("label", name)
        if check is not None:
            self.check = check
        if resolve_url is not None:
            self.resolve_url = resolve_url

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def __getitem__(self, name: str):
        node = self.get(name)
        if node is None:
            raise KeyError(f"No child with name {name} found.")
        return node

    def __iter__(self):
        yield from self.children

    def append(self, child):
        child.parent = self

    def extend(self, children):
        for child in children:
            child.parent = self

    def add_children(self, children, position=None):
        if not isinstance(children, list):
            children = list(children)

        if position is None:
            position = len(children)

        old = list(self.children)

        new = old[:position] + children + old[position:]

        # children.insert(position, child)
        self.children = new

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

    def get(self, name: str, maxlevel=None):
        return search.find_by_attr(self, value=name, maxlevel=maxlevel)

    def render(self):
        return RenderTree(self).by_attr("name")

    def process(self, request, **kwargs):
        # first check whether the menu is visible
        self.visible = (
            self.check(request, **kwargs) if callable(self.check) else self.check
        )

    def match_url(self, request):
        """
        match url determines if this is selected
        """
        self.selected = False
        if re.match(f"{self.url}$", request.path) or re.match(
            "%s" % self.url, request.path
        ):
            self.selected = True
        return self.selected


root = BaseMenu(name="DjangoFlexMenu")


class MenuItem(BaseMenu):
    template = "menu/item.html"

    def __init__(self, name: str, view_name="", url="", *args, **kwargs):
        if not url and not view_name:
            raise ValueError("Either a url or view_name must be provided")

        self.view_name = view_name
        self.url = url

        super().__init__(name, *args, **kwargs)

    def process(self, request, **kwargs):
        super().process(request, **kwargs)

        # if the menu is visible, make sure the url is resolvable
        self.url = self.resolve_url(request, **kwargs)
        if self.url is not None:
            self.visible = True
            self.match_url(request)

    def resolve_url(self, request, *args, **kwargs):
        if self.view_name:
            with suppress(NoReverseMatch):
                return reverse(self.view_name, args=args, kwargs=kwargs)
        elif self.url and callable(self.url):
            return self.url(request, *args, **kwargs)
        else:
            return self.url

    def check(self, request, **kwargs):
        # return True
        self.url = self.resolve_url(request)
        if self.url is not None:
            self.visible = True
            self.match_url(request)
        return self.url


class Menu(BaseMenu):
    root_template = "menu/base.html"
    template = "menu/menu.html"

    def __init__(self, name, parent=None, children=None, **kwargs):
        if not parent:
            parent = root
        super().__init__(name, parent, children, **kwargs)

    def process(self, request, **kwargs):
        # first check whether the menu is visible
        super().process(request, **kwargs)
        for child in self.children:
            child.process(request, **kwargs)

    def check(self, request, **kwargs):
        # return True
        self.visible = any([child.check(request) for child in self.children])
        return self.visible

    def match_url(self, request):
        """
        match url determines if this is selected
        """
        return any([child.match_url(request) for child in self.children])
