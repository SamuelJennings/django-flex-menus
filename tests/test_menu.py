import pytest


def test_menu_link_requires_template_name():
    from flex_menu.menu import MenuLink
    link = MenuLink("test", url="/test/")
    with pytest.raises(NotImplementedError):
        link.get_template_names()

def test_menu_item_requires_template_name():
    from flex_menu.menu import MenuItem
    item = MenuItem("test")
    with pytest.raises(NotImplementedError):
        item.get_template_names()

def test_menu_group_requires_template_name():
    from flex_menu.menu import MenuGroup
    group = MenuGroup("test")
    with pytest.raises(NotImplementedError):
        group.get_template_names()
"""
Improved tests for the basic menu functionality in django-flex-menus.
This replaces the original test_menu.py with better structured tests.
"""


from flex_menu.menu import MenuGroup, MenuLink


class MockUser:
    """Mock user object for testing."""

    def __init__(self):
        self.is_authenticated = True
        self.is_staff = False
        self.is_superuser = False


class MockRequest:
    """Mock request object for testing."""

    def __init__(self, path="/test/"):
        self.path = path
        self.user = MockUser()


@pytest.fixture
def menu_group():
    """Create a basic MenuGroup instance."""
    return MenuGroup(name="test_menu")


@pytest.fixture
def child_item():
    """Create a basic MenuLink instance."""
    return MenuLink(name="child_item", url="/test/")


@pytest.fixture
def child_menu():
    """Create a basic child MenuGroup instance."""
    return MenuGroup(name="child_menu")


@pytest.fixture
def mock_request():
    """Create a mock request."""
    return MockRequest()


class TestBasicMenuFunctionality:
    """Test basic menu functionality."""

    def test_menu_initialization(self, menu):
        """Test MenuGroup initialization."""
        assert menu.name == "test_menu"
        assert menu._check is True
        assert menu.extra_context == {}

    def test_menu_initialization_with_extra_context(self):
        """Test MenuGroup initialization with extra context data."""
        context_data = {"title": "Test MenuGroup", "icon": "menu-icon"}
        menu = MenuGroup(name="test_menu", extra_context=context_data)
        assert menu.extra_context == context_data
        assert menu.extra_context["title"] == "Test MenuGroup"

    def test_menu_append(self, menu, child_item):
        """Test appending a child to a menu."""
        menu.append(child_item)
        assert child_item in menu.children
        assert child_item.parent == menu

    def test_menu_extend(self, menu, child_item):
        """Test extending menu with multiple children."""
        child2 = MenuLink(name="child2", url="/child2/")
        menu.extend([child_item, child2])
        assert child_item in menu.children
        assert child2 in menu.children
        assert child_item.parent == menu
        assert child2.parent == menu

    def test_menu_insert(self, menu, child_item):
        """Test inserting a child at specific position."""
        child2 = MenuLink(name="child2", url="/child2/")
        menu.append(child_item)
        menu.insert(child2, position=0)
        children_list = list(menu.children)
        assert children_list[0] == child2
        assert children_list[1] == child_item

    def test_menu_insert_after(self, menu, child_item):
        """Test inserting a child after a named child."""
        child2 = MenuLink(name="child2", url="/child2/")
        menu.append(child_item)
        menu.insert_after(child2, named="child_item")
        children_list = list(menu.children)
        assert children_list[1] == child2

    def test_menu_pop(self, menu, child_item):
        """Test removing a child by name."""
        menu.append(child_item)
        removed_child = menu.pop("child_item")
        assert removed_child == child_item
        assert child_item not in menu.children

    def test_menu_get(self, menu, child_item):
        """Test finding a child by name."""
        menu.append(child_item)
        found_child = menu.get("child_item")
        assert found_child == child_item

    def test_menu_print_tree(self, menu, child_item):
        """Test printing menu structure."""
        menu.append(child_item)
        rendered = menu.print_tree()
        assert "test_menu" in rendered
        assert "child_item" in rendered

    def test_menu_process(self, menu, mock_request):
        """Test processing menu with request."""
        processed = menu.process(mock_request)
        assert processed.request == mock_request
        # MenuGroup without visible children should not be visible
        assert processed.visible is False

    def test_menu_match_url(self, menu, child_item, mock_request):
        """Test URL matching functionality."""
        menu.append(child_item)
        processed = menu.process(mock_request)
        # child_item has URL "/test/" which matches mock_request.path
        assert processed.match_url() is True

    def test_menu_copy(self, menu, child_item):
        """Test deep copying of menu."""
        menu.append(child_item)
        menu_copy = menu.copy()
        assert menu_copy.name == menu.name
        assert menu_copy is not menu
        assert len(menu_copy.children) == len(menu.children)


class TestMenuLinkFunctionality:
    """Test MenuLink specific functionality."""

    def test_menu_item_initialization_with_url(self):
        """Test MenuLink initialization with URL."""
        item = MenuLink(name="test_item", url="/test/")
        assert item.name == "test_item"
        assert item._url == "/test/"
        assert item.extra_context == {}

    def test_menu_item_initialization_with_extra_context(self):
        """Test MenuLink initialization with extra context data."""
        context_data = {"label": "Test Item", "badge": "New"}
        item = MenuLink(name="test_item", url="/test/", extra_context=context_data)
        assert item.extra_context == context_data
        assert item.extra_context["label"] == "Test Item"

    def test_menu_item_initialization_with_view_name(self):
        """Test MenuLink initialization with view name."""
        item = MenuLink(name="test_item", view_name="test_view")
        assert item.name == "test_item"
        assert item.view_name == "test_view"

    def test_menu_item_initialization_invalid(self):
        """Test MenuLink initialization without URL or view name fails."""
        with pytest.raises(
            ValueError, match="Either a url or view_name must be provided"
        ):
            MenuLink(name="test_item")

    def test_menu_item_process_visible(self, mock_request):
        """Test processing visible MenuLink."""
        item = MenuLink(name="test_item", url="/test/", check=True)
        processed = item.process(mock_request)
        assert processed.visible is True
        assert processed.url == "/test/"
        assert processed.selected is True  # URL matches request path

    def test_menu_item_process_invisible(self, mock_request):
        """Test processing invisible MenuLink."""
        item = MenuLink(name="test_item", url="/test/", check=False)
        processed = item.process(mock_request)
        assert processed.visible is False

    def test_menu_item_resolve_url_static(self):
        """Test resolving static URL."""
        item = MenuLink(name="test_item", url="/static/")
        resolved_url = item.resolve_url()
        assert resolved_url == "/static/"

    def test_menu_item_resolve_url_with_params(self):
        """Test resolving URL with parameters."""
        item = MenuLink(name="test_item", url="/test/", params={"id": "123"})
        resolved_url = item.resolve_url()
        assert resolved_url == "/test/?id=123"


class TestMenuHierarchy:
    """Test menu hierarchy functionality."""

    def test_nested_menu_structure(self):
        """Test creating nested menu structures."""
        main_menu = MenuGroup(name="main")
        submenu = MenuGroup(name="submenu")
        item = MenuLink(name="item", url="/item/")

        main_menu.append(submenu)
        submenu.append(item)

        assert submenu in main_menu.children
        assert submenu.parent == main_menu
        assert item in submenu.children
        assert item.parent == submenu

    def test_menu_visibility_propagation(self, mock_request):
        """Test that menu visibility depends on children."""
        main_menu = MenuGroup(name="main")
        visible_item = MenuLink(name="visible", url="/visible/", check=True)
        invisible_item = MenuLink(name="invisible", url="/invisible/", check=False)

        main_menu.extend([visible_item, invisible_item])

        processed = main_menu.process(mock_request)
        # Should be visible because it has at least one visible child
        assert processed.visible is True
        # Should have only one visible child
        assert len(processed._processed_children) == 1
        assert processed._processed_children[0].name == "visible"

    def test_deeply_nested_menu_search(self):
        """Test searching in deeply nested menu structures."""
        root = MenuGroup(name="root")
        level1 = MenuGroup(name="level1")
        level2 = MenuGroup(name="level2")
        deep_item = MenuLink(name="deep_item", url="/deep/")

        root.append(level1)
        level1.append(level2)
        level2.append(deep_item)

        # Should find deep item from root
        found = root.get("deep_item")
        assert found == deep_item

        # Should find intermediate level
        found_level = root.get("level2")
        assert found_level == level2


class TestMenuEdgeCases:
    """Test edge cases and error conditions."""

    def test_menu_with_no_children(self, mock_request):
        """Test menu with no children."""
        empty_menu = MenuGroup(name="empty")
        processed = empty_menu.process(mock_request)
        assert processed.visible is False

    def test_menu_with_all_invisible_children(self, mock_request):
        """Test menu where all children are invisible."""
        menu = MenuGroup(name="all_invisible")
        item1 = MenuLink(name="item1", url="/item1/", check=False)
        item2 = MenuLink(name="item2", url="/item2/", check=False)
        menu.extend([item1, item2])

        processed = menu.process(mock_request)
        assert processed.visible is False
        assert len(processed._processed_children) == 0

    def test_menu_item_nonexistent_get(self, menu):
        """Test getting nonexistent child returns None."""
        found = menu.get("nonexistent")
        assert found is None

    def test_menu_item_pop_nonexistent(self, menu):
        """Test popping nonexistent child raises ValueError."""
        with pytest.raises(ValueError, match="No child with name nonexistent found"):
            menu.pop("nonexistent")

    def test_insert_after_nonexistent(self, menu):
        """Test inserting after nonexistent child raises ValueError."""
        item = MenuLink(name="new_item", url="/new/")
        with pytest.raises(ValueError, match="No child with name 'nonexistent' found"):
            menu.insert_after(item, named="nonexistent")


class TestMenuWithCustomChecks:
    """Test menus with custom check functions."""

    def test_menu_with_custom_check_function(self, mock_request):
        """Test menu with custom check function."""

        def custom_check(request, **kwargs):
            return request.path == "/test/"

        menu = MenuGroup(name="custom", check=custom_check)
        item = MenuLink(name="item", url="/item/")
        menu.append(item)

        processed = menu.process(mock_request)
        assert processed.visible is True  # Custom check should pass

    def test_menu_item_with_custom_check(self, mock_request):
        """Test menu item with custom check function."""

        def custom_check(request, **kwargs):
            return hasattr(request.user, "special_access")

        item = MenuLink(name="special", url="/special/", check=custom_check)

        # Without special access
        processed = item.process(mock_request)
        assert processed.visible is False

        # With special access
        mock_request.user.special_access = True
        processed = item.process(mock_request)
        assert processed.visible is True

    def test_menu_with_failing_check(self, mock_request):
        """Test menu with check that returns False."""
        menu = MenuGroup(name="failing", check=False)
        item = MenuLink(name="item", url="/item/")
        menu.append(item)

        processed = menu.process(mock_request)
        # Even though item would be visible, menu check fails
        assert processed.visible is False


class TestMenuContextData:
    """Test menu context data functionality."""

    def test_base_menu_get_context_data(self):
        """Test BaseMenu get_context_data method."""
        extra_context = {"title": "Test MenuGroup", "icon": "fa-menu"}
        menu = MenuGroup(name="test", extra_context=extra_context)

        context = menu.get_context_data()

        assert "menu" in context
        assert context["menu"] == menu
        assert context["title"] == "Test MenuGroup"
        assert context["icon"] == "fa-menu"

    def test_base_menu_get_context_data_with_kwargs(self):
        """Test BaseMenu get_context_data with additional kwargs."""
        extra_context = {"title": "Test MenuGroup"}
        menu = MenuGroup(name="test", extra_context=extra_context)

        context = menu.get_context_data(
            request_specific="value", override_title="New Title"
        )

        assert context["title"] == "Test MenuGroup"  # extra_context comes first
        assert context["request_specific"] == "value"
        assert context["override_title"] == "New Title"

    def test_menu_item_get_context_data(self, mock_request):
        """Test MenuLink get_context_data method."""
        extra_context = {"label": "Home", "badge": "New"}
        item = MenuLink(name="home", url="/home/", extra_context=extra_context)

        # Process the item to set URL and selection state
        processed = item.process(mock_request)

        context = processed.get_context_data()

        assert "menu" in context
        assert context["menu"] == processed
        assert context["label"] == "Home"
        assert context["badge"] == "New"
        assert "url" in context
        assert "is_selected" in context
        assert "view_name" in context
        assert "params" in context

    def test_menu_get_context_data_with_children(self, mock_request):
        """Test MenuGroup get_context_data includes children information."""
        menu = MenuGroup(name="main")
        item1 = MenuLink(name="item1", url="/item1/")
        item2 = MenuLink(name="item2", url="/item2/", check=False)  # invisible
        menu.extend([item1, item2])

        processed = menu.process(mock_request)
        context = processed.get_context_data()

        assert "children" in context
        assert "has_visible_children" in context
        assert context["has_visible_children"] is True
        assert len(context["children"]) == 1  # Only visible children

    def test_context_data_copying_during_processing(self, mock_request):
        """Test that extra_context is properly copied during processing."""
        original_context = {"title": "Original", "mutable_list": [1, 2, 3]}
        menu = MenuGroup(name="test", extra_context=original_context)

        processed = menu.process(mock_request)

        # Modify the processed menu's context
        processed.extra_context["title"] = "Modified"
        processed.extra_context["mutable_list"].append(4)

        # Original should be unchanged for the title (string is immutable)
        # but list will be shared (shallow copy)
        assert menu.extra_context["title"] == "Original"
        assert menu.extra_context["mutable_list"] == [
            1,
            2,
            3,
            4,
        ]  # Shared reference

    def test_empty_extra_context(self):
        """Test menu with no extra context data."""
        menu = MenuGroup(name="test")

        context = menu.get_context_data()

        assert "menu" in context
        assert context["menu"] == menu
        # Should only have the menu itself, no additional context

    def test_override_get_context_data(self, mock_request):
        """Test overriding get_context_data in a custom menu class."""

        class CustomMenuLink(MenuLink):
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context.update(
                    {
                        "computed_value": self.name.upper(),
                        "has_request": self.request is not None,
                    }
                )
                return context

        item = CustomMenuLink(name="custom", url="/custom/")
        processed = item.process(mock_request)

        context = processed.get_context_data()

        assert context["computed_value"] == "CUSTOM"
        assert context["has_request"] is True
