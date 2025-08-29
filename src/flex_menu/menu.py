import copy
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Optional, Union
from urllib.parse import urlencode

from anytree import Node, RenderTree, search
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.safestring import mark_safe

if TYPE_CHECKING:
    from typing import Type


# Configuration for logging URL resolution failures
def _should_log_url_failures():
    """
    Check if URL resolution failures should be logged.

    By default, URL failures are only logged when DEBUG=True since failed
    URL resolution is often expected behavior (e.g., menu items that should
    be hidden when users lack permissions or when optional views aren't available).

    Can be overridden with the FLEX_MENU_LOG_URL_FAILURES setting.

    Returns:
        bool: True if URL failures should be logged, False otherwise.
    """
    return getattr(settings, "FLEX_MENU_LOG_URL_FAILURES", settings.DEBUG)


class BaseMenu(Node):
    """Represents a base menu structure with hierarchical nodes.

    Inherits from `anytree.Node` and provides additional functionality
    for dynamic menu construction, URL resolution, and visibility checking.

    Attributes:
        visible (bool): Whether the menu is visible, determined during processing.
        selected (bool): Whether the menu item matches the current request path.
        template (str): The template used for rendering this menu.
        allowed_children (List[type]): List of allowed child classes. None means any BaseMenu subclass is allowed.
                                      Use the string "self" to allow instances of the exact same class as the parent
                                      (inheritance is not considered for "self" references).
        extra_context (dict): Additional context data for template rendering.
    """

    request: WSGIRequest | None
    template_name = None  # Must be defined in subclasses
    allowed_children: list[Union["Type[BaseMenu]", str]] | None = None  # None means allow any BaseMenu subclass

    def __init__(
        self,
        name: str,
        parent: Optional["BaseMenu"] = None,
        children: list["BaseMenu"] | None = None,
        check: Callable | bool = True,
        resolve_url: Callable | None = None,
        template_name: str | None = None,
        extra_context: dict | None = None,
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
            template_name (Optional[str]): Custom template for this menu item.
            extra_context (Optional[dict]): Additional context data for template rendering.
            **kwargs: Additional attributes for the node.
        """
        super().__init__(name, parent=parent, children=children, **kwargs)
        self._check = check
        self.extra_context = extra_context or {}

        # Set template (use provided template or keep class default)
        if template_name is not None:
            self.template_name = template_name

        # Initialize state attributes
        self.visible = False
        self.selected = False
        self.request: WSGIRequest | None = None

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

    def _validate_child(self, child: "BaseMenu") -> None:
        """Validate that a child is of an allowed type or subclass.

        Args:
            child: The child menu to validate

        Raises:
            TypeError: If child is not of an allowed type or subclass thereof
        """
        if not isinstance(child, BaseMenu):
            raise TypeError(f"Child must be a BaseMenu instance, got {type(child)}")

        if self.allowed_children is not None:
            # Build list of actual allowed types, handling self-references
            allowed_types: list[type] = []
            allowed_names: list[str] = []
            exact_class_matches: list[bool] = []  # Track which types require exact class matching

            for allowed_type in self.allowed_children:
                if allowed_type == "self":
                    # Allow instances of the same class as the parent (exact match only)
                    allowed_types.append(self.__class__)
                    allowed_names.append(self.__class__.__name__)
                    exact_class_matches.append(True)
                else:
                    # allowed_type should be a class type here
                    if isinstance(allowed_type, str):
                        raise TypeError(
                            f"Invalid allowed_children entry: {allowed_type}. Only 'self' string is allowed."
                        )
                    allowed_types.append(allowed_type)
                    allowed_names.append(allowed_type.__name__)
                    exact_class_matches.append(False)

            # Check if child matches any allowed type
            is_allowed = False
            for allowed_type, exact_match in zip(allowed_types, exact_class_matches):
                if exact_match:
                    # For "self" references, require exact class match
                    if type(child) is allowed_type:
                        is_allowed = True
                        break
                else:
                    # For regular types, allow inheritance
                    if isinstance(child, allowed_type):
                        is_allowed = True
                        break

            if not is_allowed:
                raise TypeError(
                    f"{self.__class__.__name__} only allows children of types {allowed_names} "
                    f"(or their subclasses), but got {type(child).__name__}"
                )

    def append(self, child: "BaseMenu") -> None:
        """Appends a child node to the current menu.

        Args:
            child (BaseMenu): The child menu node.

        Raises:
            TypeError: If the child type is not allowed.
        """
        self._validate_child(child)
        child.parent = self  # type: ignore[has-type]

    def extend(self, children: list["BaseMenu"]) -> None:
        """Appends multiple child nodes to the current menu.

        Args:
            children (List[BaseMenu]): A list of child nodes.

        Raises:
            TypeError: If any child type is not allowed.
        """
        # Validate all children first before adding any
        for child in children:
            self._validate_child(child)

        # If validation passes, add all children
        for child in children:
            child.parent = self  # type: ignore[has-type]

    def insert(
        self,
        children: Union["BaseMenu", list["BaseMenu"]],
        position: int,
    ) -> None:
        """Inserts child nodes at a specified position.

        Args:
            children (Union[BaseMenu, List[BaseMenu]]): A child or list of child nodes.
            position (int): Position to insert at.

        Raises:
            TypeError: If any child type is not allowed.
        """
        if not isinstance(children, list):
            children = [children]

        # Validate all children first
        for child in children:
            self._validate_child(child)

        old = list(self.children)  # type: ignore[has-type]
        new = old[:position] + children + old[position:]
        self.children = new

    def insert_after(self, child: "BaseMenu", named: str) -> None:
        """Inserts a child node after an existing child with a specified name.

        Args:
            child (BaseMenu): The new child node to insert.
            named (str): The name of the existing child after which to insert.

        Raises:
            ValueError: If no child with the specified name exists.
            TypeError: If the child is not a valid menu item or allowed type.
        """
        self._validate_child(child)

        existing_child = self.get(named)
        if existing_child:
            children_list = list(self.children)
            insert_index = children_list.index(existing_child) + 1
            self.children = children_list[:insert_index] + [child] + children_list[insert_index:]
        else:
            raise ValueError(f"No child with name '{named}' found.")

    def pop(self, name: str | None = None) -> "BaseMenu":
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
                node.parent = None  # type: ignore[has-type]
                return node
            else:
                raise ValueError(f"No child with name {name} found.")
        self.parent = None
        return self

    def get(self, name: str, maxlevel: int | None = None) -> Optional["BaseMenu"]:
        """Finds a child node by name.

        Args:
            name (str): The name of the child node to find.
            maxlevel (Optional[int]): The maximum depth to search.
                                     1 = direct children only, 2 = children and grandchildren, etc.

        Returns:
            Optional[BaseMenu]: The child node, or None if not found.
        """
        if not name:
            return None

        # Adjust maxlevel for anytree's 1-indexed counting from search root
        # maxlevel=1 should search direct children, so we need anytree maxlevel=2
        anytree_maxlevel = maxlevel + 1 if maxlevel is not None else None

        result = search.find_by_attr(self, value=name, name="name", maxlevel=anytree_maxlevel)
        return result  # type: ignore[no-any-return]

    def print_tree(self) -> str:
        """Prints the menu tree structure.

        Returns:
            str: A string representation of the tree.
        """
        result = RenderTree(self).by_attr("name")
        return str(result)

    def process(self, request, **kwargs) -> "BaseMenu":
        """Processes the visibility of the menu based on a request.

        Returns a processed copy to avoid race conditions between concurrent requests.

        Args:
            request: The HTTP request object.
            **kwargs: Additional arguments for the check function.

        Returns:
            BaseMenu: A processed copy of this menu with request-specific state.
        """
        # Create a shallow copy to avoid mutating the shared instance
        processed = self._create_request_copy()
        processed.request = request
        processed.visible = processed.check(request, **kwargs)
        return processed

    def _create_request_copy(self) -> "BaseMenu":
        """Create a shallow copy for request processing without copying children."""
        # Create new instance with same configuration but fresh state
        copy_instance = self.__class__(
            name=self.name,
            check=self._check,
            extra_context=self.extra_context.copy(),
        )
        # Copy static attributes but not request-specific state
        for attr in ["params", "view_name", "_url", "template_name"]:
            if hasattr(self, attr):
                setattr(copy_instance, attr, getattr(self, attr))
        return copy_instance

    def check(self, request, **kwargs) -> bool:
        """Checks if the menu item is visible based on the request.

        Args:
            request: The HTTP request object.
            **kwargs: Additional arguments for custom check functions.

        Returns:
            bool: True if the menu item is visible, False otherwise.
        """
        if callable(self._check):
            result = self._check(request, **kwargs)
            return bool(result)
        return bool(self._check)

    def get_context_data(self, **kwargs) -> dict:
        """
        Get context data for template rendering.

        This method mirrors Django's View.get_context_data() pattern and can be
        overridden in subclasses to provide dynamic, request-aware context data.

        Args:
            **kwargs: Additional context data passed from the caller.

        Returns:
            dict: A dictionary containing context data for template rendering.
                 Includes the menu instance itself and any extra_context.
        """
        context = {
            "menu": self,
            **self.extra_context,
            **kwargs,
        }
        return context

    def get_template_names(self) -> list[str]:
        """
        Get the template names for rendering this menu.

        Returns:
            List[str]: A list of template paths for rendering.

        Raises:
            NotImplementedError: If template_name is None, indicating that subclasses
                                must define a template_name.
        """
        if self.template_name is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define a 'template_name' class attribute. "
                f"Set template_name = 'path/to/template.html' in your class definition."
            )
        return [self.template_name]

    def render(self, **kwargs):
        """
        Render the menu using its template and context data.

        The template receives the menu/item instance in context and can
        recursively render children by calling child.render() in a loop.

        Args:
            **kwargs: Additional context data passed to get_context_data().

        Returns:
            str: The rendered HTML string, or empty string if not visible.
        """
        if not self.visible:
            return ""

        context = self.get_context_data(**kwargs)
        return mark_safe(
            render_to_string(
                self.get_template_names(),
                context,
            )
        )

    def match_url(self) -> bool:
        """Checks if the menu item's URL matches the request path.

        Returns:
            bool: True if the URL matches the request path, False otherwise.
        """
        url = getattr(self, "url", None)
        if not url or not self.request:
            self.selected = False
            return False

        self.selected = url == self.request.path
        return self.selected

    def copy(self) -> "BaseMenu":
        """Creates a deep copy of the menu.

        Warning: This operation is expensive and should be avoided during
        request processing. Use only for menu setup/configuration.

        Returns:
            BaseMenu: A new deep copy of the current menu.
        """
        return copy.deepcopy(self)


root = BaseMenu(name="DjangoFlexMenu")

# Sentinel value to distinguish between "no parent specified" and "explicitly no parent"
_NO_PARENT = object()


class MenuLink(BaseMenu):
    template_name = "menu/item.html"

    def __init__(
        self,
        name: str,
        view_name: str = "",
        url: str = "",
        params: dict | None = None,
        template_name: str | None = None,
        extra_context: dict | None = None,
        **kwargs,
    ):
        if not url and not view_name:
            raise ValueError("Either a url or view_name must be provided")
        self.params = params or {}
        self.view_name = view_name
        self._url = url
        self.url = None  # Will be set during processing

        super().__init__(
            name,
            template_name=template_name,
            extra_context=extra_context,
            **kwargs,
        )

    def process(self, request, **kwargs):
        # Create processed copy to avoid race conditions
        processed = self._create_request_copy()
        processed.request = request
        processed.visible = processed.check(request, **kwargs)

        if not processed.visible:
            # didn't pass the check, no need to continue
            return processed

        # if the menu is visible, make sure the url is resolvable
        processed.url = processed.resolve_url(**kwargs)
        if processed.url:
            processed.match_url()
        else:
            # If URL cannot be resolved, hide the menu item
            processed.visible = False

        return processed

    def resolve_url(self, *args, **kwargs):
        # Simple caching for static URLs (no args/kwargs)
        if not args and not kwargs and hasattr(self, "_cached_url"):
            return self._cached_url

        if self.view_name:
            try:
                url = reverse(self.view_name, args=args, kwargs=kwargs)
                # Cache static URLs for reuse
                if not args and not kwargs:
                    self._cached_url = url
                return url
            except NoReverseMatch:
                # Only log if explicitly configured to do so
                if _should_log_url_failures():
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Could not reverse URL for view '{self.view_name}' in menu item '{self.name}'")
                # Cache failure for static URLs
                if not args and not kwargs:
                    self._cached_url = None
                return None

        elif self._url and callable(self._url):
            try:
                return self._url(self.request, *args, **kwargs)
            except Exception as e:
                # Only log if explicitly configured to do so
                if _should_log_url_failures():
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Error calling URL function for menu item '{self.name}': {e}")
                return None

        elif self._url:
            if self.params:
                query_string = urlencode(self.params)
                separator = "&" if "?" in self._url else "?"
                url = self._url + separator + query_string
            else:
                url = self._url

            # Cache static URLs for reuse (when no args/kwargs)
            if not args and not kwargs:
                self._cached_url = url
            return url

        return None

    def get_context_data(self, **kwargs) -> dict:
        """
        Get context data for template rendering.

        Extends the base implementation to include URL and selection information.

        Args:
            **kwargs: Additional context data passed from the caller.

        Returns:
            dict: A dictionary containing context data for template rendering.
        """
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "url": getattr(self, "url", None),
                "is_selected": getattr(self, "selected", False),
                "view_name": getattr(self, "view_name", ""),
                "params": getattr(self, "params", {}),
            }
        )
        return context

    def _create_request_copy(self) -> "MenuLink":
        """Create a shallow copy for request processing without copying children."""
        # Create new instance with same configuration but fresh state
        copy_instance = self.__class__(
            name=self.name,
            view_name=self.view_name,
            url=self._url,
            params=self.params,
            check=self._check,
            extra_context=self.extra_context.copy(),
        )
        # Copy additional attributes
        for attr in ["template_name", "_cached_url"]:
            if hasattr(self, attr):
                setattr(copy_instance, attr, getattr(self, attr))
        return copy_instance


class MenuItem(BaseMenu):
    """A menu item that doesn't provide a link - used for non-clickable menu items like headers or separators."""

    template_name = None

    def __init__(
        self,
        name: str,
        template_name: str | None = None,
        extra_context: dict | None = None,
        **kwargs,
    ):
        super().__init__(
            name,
            template_name=template_name,
            extra_context=extra_context,
            **kwargs,
        )

    def _create_request_copy(self) -> "MenuItem":
        """Create a shallow copy for request processing without copying children."""
        copy_instance = self.__class__(
            name=self.name,
            check=self._check,
            extra_context=self.extra_context.copy(),
        )
        # Copy template attribute
        copy_instance.template_name = getattr(self, "template_name", "")
        return copy_instance


class MenuGroup(BaseMenu):
    template_name = "menu/menu.html"

    def __init__(
        self,
        name,
        parent=None,
        children=None,
        template_name=None,
        extra_context=None,
        **kwargs,
    ):
        if parent is None:
            parent = root
        elif parent is _NO_PARENT:
            parent = None
        super().__init__(
            name,
            parent,
            children,
            template_name=template_name,
            extra_context=extra_context,
            **kwargs,
        )
        self._processed_children = []

    def process(self, request, **kwargs):
        # Create processed copy to avoid race conditions
        processed = self._create_request_copy()
        processed.request = request

        # Process children and attach to processed copy
        processed_children = []
        for child in self.children:
            processed_child = child.process(request, **kwargs)
            if processed_child and processed_child.visible:  # Only include visible children
                processed_children.append(processed_child)

        # Set children on processed copy (avoiding anytree parent/child mutation)
        processed._processed_children = processed_children

        # Now check visibility based on processed children
        processed.visible = processed.check(request, **kwargs)

        return processed

    @property
    def processed_children(self):
        """
        Public property to access processed children for templates.
        Falls back to regular children if no processed children exist.
        """
        return getattr(self, "_processed_children", self.children)

    def get_context_data(self, **kwargs) -> dict:
        """
        Get context data for template rendering.

        Extends the base implementation to include processed children information.

        Args:
            **kwargs: Additional context data passed from the caller.

        Returns:
            dict: A dictionary containing context data for template rendering.
        """
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "children": self.processed_children,
                "has_visible_children": bool(self.processed_children),
            }
        )
        return context

    def _create_request_copy(self) -> "MenuGroup":
        """Create a shallow copy for request processing."""
        copy_instance = self.__class__(
            name=self.name,
            check=self._check,
            parent=_NO_PARENT,  # Explicitly no parent to avoid auto-adding to root
            extra_context=self.extra_context.copy(),
        )
        # Copy template attribute
        copy_instance.template_name = getattr(self, "template_name", "")
        copy_instance._processed_children = []
        return copy_instance

    def check(self, request, **kwargs) -> bool:
        """
        Check if the menu should be visible.

        For processed copies, check children from _processed_children.
        For original instances, check actual children.

        Args:
            request: The HTTP request object.
            **kwargs: Additional arguments.

        Returns:
            bool: True if menu should be visible, False otherwise.
        """
        # First check the menu's own check function
        own_check_result = super().check(request, **kwargs)
        if not own_check_result:
            return False

        # If the menu's own check passes, check if it has visible children
        children_to_check = getattr(self, "_processed_children", self.children)
        if not children_to_check:
            return False

        return any(child.check(request, **kwargs) for child in children_to_check)

    def match_url(self) -> bool:
        """
        Check if any child menu item matches the current URL.

        Returns:
            bool: True if any child is selected, False otherwise.
        """
        if not hasattr(self, "request") or not self.request:
            return False

        children_to_check = getattr(self, "_processed_children", self.children)
        return any(child.match_url() for child in children_to_check)
