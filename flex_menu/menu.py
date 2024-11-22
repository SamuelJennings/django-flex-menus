import copy
import re
from contextlib import suppress
from typing import Callable, List, Optional, Union

from anytree import Node, RenderTree, search
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch


class BaseMenu(Node):
    """Represents a base menu structure with hierarchical nodes.

    Inherits from `anytree.Node` and provides additional functionality
    for dynamic menu construction, URL resolution, and visibility checking.

    Attributes:
        label (str): The display label for the menu item.
        visible (bool): Whether the menu is visible, determined during processing.
        selected (bool): Whether the menu item matches the current request path.
    """

    def __init__(
        self,
        name: str,
        parent: Optional["BaseMenu"] = None,
        children: Optional[List["BaseMenu"]] = None,
        check: Union[Callable, bool] = True,
        resolve_url: Optional[Callable] = None,
        **kwargs,
    ):
        """
        Initializes a new menu node.

        Args:
            name (str): The unique name of the menu item.
            parent (Optional[BaseMenu]): The parent menu item.
            children (Optional[List[BaseMenu]]): List of child menu items.
            check (Optional[Callable]): A callable that determines if the menu is visible.
            resolve_url (Optional[Callable]): A callable to resolve the menu item's URL.
            **kwargs: Additional attributes for the node.
        """
        super().__init__(name, parent=parent, children=children, **kwargs)
        self.label = kwargs.get("label", name)
        if check is not None:
            self.check = check
        if resolve_url is not None:
            self.resolve_url = resolve_url

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"

    def __getitem__(self, name: str) -> "BaseMenu":
        node = self.get(name)
        if node is None:
            raise KeyError(f"No child with name {name} found.")
        return node

    def __iter__(self):
        yield from self.children

    def append(self, child: "BaseMenu") -> None:
        """Appends a child node to the current menu.

        Args:
            child (BaseMenu): The child menu node.
        """
        child.parent = self

    def extend(self, children: List["BaseMenu"]) -> None:
        """Appends multiple child nodes to the current menu.

        Args:
            children (List[BaseMenu]): A list of child nodes.
        """
        for child in children:
            child.parent = self

    def insert(
        self,
        children: Union["BaseMenu", List["BaseMenu"]],
        position: int,
    ) -> None:
        """Inserts child nodes at a specified position.

        Args:
            children (Union[BaseMenu, List[BaseMenu]]): A child or list of child nodes.
            position (Optional[int]): Position to insert at. Defaults to the end.
        """
        if not isinstance(children, list):
            children = [children]

        old = list(self.children)
        new = old[:position] + children + old[position:]
        self.children = new

    def insert_after(self, child: "BaseMenu", named: str) -> None:
        """Inserts a child node after an existing child with a specified name.

        Args:
            child (BaseMenu): The new child node to insert.
            named (str): The name of the existing child after which to insert.

        Raises:
            ValueError: If no child with the specified name exists.
            TypeError: If the child is not a valid menu item.
        """
        existing_child = self.get(named)
        if existing_child:
            child.parent = self
            child._move_after(existing_child)
        else:
            raise ValueError(f"No child with name {named} found.")

    def pop(self, name: Optional[str] = None) -> "BaseMenu":
        """Removes a child node or detaches the current node from its parent.

        Args:
            name (Optional[str]): The name of the child to remove. If None, removes this node.

        Returns:
            BaseMenu: The removed node.

        Raises:
            ValueError: If no child with the specified name exists.
        """
        if name:
            node = self.get(name)
            if node:
                node.parent = None
                return node
            else:
                raise ValueError(f"No child with name {name} found.")
        self.parent = None
        return self

    def get(self, name: str, maxlevel: Optional[int] = None) -> Optional["BaseMenu"]:
        """Finds a child node by name.

        Args:
            name (str): The name of the child node to find.
            maxlevel (Optional[int]): The maximum depth to search.

        Returns:
            Optional[BaseMenu]: The child node, or None if not found.
        """
        return search.find_by_attr(self, value=name, maxlevel=maxlevel)

    def render(self) -> str:
        """Renders the menu tree structure.

        Returns:
            str: A string representation of the tree.
        """
        return RenderTree(self).by_attr("name")

    def process(self, request, **kwargs) -> None:
        """Processes the visibility of the menu based on a request.

        Args:
            request: The HTTP request object.
            **kwargs: Additional arguments for the check function.
        """
        self.visible = (
            self.check(request, **kwargs) if callable(self.check) else self.check
        )

    def match_url(self, request) -> bool:
        """Checks if the menu item's URL matches the request path.

        Args:
            request: The HTTP request object.

        Returns:
            bool: True if the URL matches the request path, False otherwise.
        """
        self.selected = bool(
            re.match(f"{self.url}$", request.path)
            or re.match(f"{self.url}", request.path)
        )
        return self.selected

    def copy(self) -> "BaseMenu":
        """Creates a deep copy of the menu.

        Returns:
            BaseMenu: A new deep copy of the current menu.
        """
        return copy.deepcopy(self)


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

        if not self.visible:
            # didn't pass the check, no need to continue
            return

        # if the menu is visible, make sure the url is resolvable
        self.url = self.resolve_url(request, **kwargs)
        if self.url and self.visible:
            self.match_url(request)
        else:
            self.visible = False

    def resolve_url(self, request, *args, **kwargs):
        if self.view_name:
            with suppress(NoReverseMatch):
                return reverse(self.view_name, args=args, kwargs=kwargs)
        elif self.url and callable(self.url):
            return self.url(request, *args, **kwargs)
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
