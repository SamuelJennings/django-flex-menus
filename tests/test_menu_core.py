"""
Comprehensive tests for the core menu functionality in django-flex-menus.
"""

from unittest.mock import patch

import pytest

from flex_menu.menu import BaseMenu, MenuGroup, MenuLink


class TestBaseMenu:
    """Test the BaseMenu class functionality."""

    def test_initialization(self):
        """Test BaseMenu initialization with various parameters."""
        menu = BaseMenu(name="test_menu", template_name="menu/base.html")
        assert menu.name == "test_menu"
        assert menu._check is True
        assert menu.visible is False
        assert menu.selected is False
        assert menu.request is None
        assert menu.template_name == "menu/base.html"
        assert menu.extra_context == {}

    def test_initialization_with_custom_params(self):
        """Test BaseMenu initialization with custom parameters."""

        def custom_check(request, **kwargs):
            return True

        def custom_resolve_url():
            return "/custom/"

        extra_context = {"title": "Custom MenuGroup", "icon": "fa-custom"}

        menu = BaseMenu(
            name="custom_menu",
            check=custom_check,
            resolve_url=custom_resolve_url,
            template_name="custom/template.html",
            extra_context=extra_context,
            custom_attr="test",
        )

        assert menu.name == "custom_menu"
        assert menu._check == custom_check
        assert menu.template_name == "custom/template.html"
        assert menu.custom_attr == "test"
        assert menu.extra_context == extra_context

    def test_string_representation(self):
        """Test string representation of BaseMenu."""
        menu = BaseMenu(name="test", template_name="menu/base.html")
        assert str(menu) == "BaseMenu(name=test)"

    def test_getitem_access(self):
        """Test accessing children via __getitem__."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child = BaseMenu(name="child", template_name="menu/base.html")
        parent.append(child)

        assert parent["child"] == child

        with pytest.raises(KeyError):
            parent["nonexistent"]

    def test_iteration(self):
        """Test iterating over menu children."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child1 = BaseMenu(name="child1", template_name="menu/base.html")
        child2 = BaseMenu(name="child2", template_name="menu/base.html")
        parent.extend([child1, child2])

        children = list(parent)
        assert len(children) == 2
        assert child1 in children
        assert child2 in children

    def test_append(self):
        """Test appending a child to a menu."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child = BaseMenu(name="child", template_name="menu/base.html")

        parent.append(child)

        assert child in parent.children
        assert child.parent == parent

    def test_extend(self):
        """Test extending a menu with multiple children."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child1 = BaseMenu(name="child1", template_name="menu/base.html")
        child2 = BaseMenu(name="child2", template_name="menu/base.html")

        parent.extend([child1, child2])

        assert child1 in parent.children
        assert child2 in parent.children
        assert child1.parent == parent
        assert child2.parent == parent

    def test_insert(self):
        """Test inserting children at specific positions."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child1 = BaseMenu(name="child1", template_name="menu/base.html")
        child2 = BaseMenu(name="child2", template_name="menu/base.html")
        child3 = BaseMenu(name="child3", template_name="menu/base.html")

        parent.append(child1)
        parent.append(child3)
        parent.insert(child2, position=1)

        children = list(parent.children)
        assert children[0] == child1
        assert children[1] == child2
        assert children[2] == child3

    def test_insert_multiple(self):
        """Test inserting multiple children at once."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child1 = BaseMenu(name="child1", template_name="menu/base.html")
        child2 = BaseMenu(name="child2", template_name="menu/base.html")
        child3 = BaseMenu(name="child3", template_name="menu/base.html")
        child4 = BaseMenu(name="child4", template_name="menu/base.html")

        parent.extend([child1, child4])
        parent.insert([child2, child3], position=1)

        children = list(parent.children)
        assert children[0] == child1
        assert children[1] == child2
        assert children[2] == child3
        assert children[3] == child4

    def test_insert_after(self):
        """Test inserting a child after a named child."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child1 = BaseMenu(name="child1", template_name="menu/base.html")
        child2 = BaseMenu(name="child2", template_name="menu/base.html")
        child3 = BaseMenu(name="child3", template_name="menu/base.html")

        parent.extend([child1, child3])
        parent.insert_after(child2, named="child1")

        children = list(parent.children)
        assert children[0] == child1
        assert children[1] == child2
        assert children[2] == child3

    def test_insert_after_nonexistent(self):
        """Test inserting after a nonexistent child raises ValueError."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child = BaseMenu(name="child", template_name="menu/base.html")

        with pytest.raises(ValueError, match="No child with name 'nonexistent' found"):
            parent.insert_after(child, named="nonexistent")

    def test_pop_by_name(self):
        """Test removing a child by name."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child = BaseMenu(name="child", template_name="menu/base.html")
        parent.append(child)

        removed = parent.pop("child")

        assert removed == child
        assert child not in parent.children
        assert child.parent is None

    def test_pop_self(self):
        """Test removing self from parent."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child = BaseMenu(name="child", template_name="menu/base.html")
        parent.append(child)

        removed = child.pop()

        assert removed == child
        assert child not in parent.children
        assert child.parent is None

    def test_pop_nonexistent(self):
        """Test popping a nonexistent child raises ValueError."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")

        with pytest.raises(ValueError, match="No child with name nonexistent found"):
            parent.pop("nonexistent")

    def test_get(self):
        """Test finding children by name."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child = BaseMenu(name="child", template_name="menu/base.html")
        grandchild = BaseMenu(name="grandchild", template_name="menu/base.html")
        parent.append(child)
        child.append(grandchild)

        # Direct child
        assert parent.get("child") == child

        # Grandchild (recursive search)
        assert parent.get("grandchild") == grandchild

        # Nonexistent
        assert parent.get("nonexistent") is None

    def test_get_with_maxlevel(self):
        """Test finding children with depth limitation."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child = BaseMenu(name="child", template_name="menu/base.html")
        grandchild = BaseMenu(name="grandchild", template_name="menu/base.html")
        parent.append(child)
        child.append(grandchild)

        # Should find direct child
        assert parent.get("child", maxlevel=1) == child

        # Should not find grandchild with maxlevel=1
        assert parent.get("grandchild", maxlevel=1) is None

    def test_print_tree(self):
        """Test printing menu tree structure."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child1 = BaseMenu(name="child1", template_name="menu/base.html")
        child2 = BaseMenu(name="child2", template_name="menu/base.html")
        parent.extend([child1, child2])

        rendered = parent.print_tree()
        assert "parent" in rendered
        assert "child1" in rendered
        assert "child2" in rendered

    def test_process_basic(self, mock_request):
        """Test basic processing of menu visibility."""
        menu = BaseMenu(name="test", check=True, template_name="menu/base.html")

        processed = menu.process(mock_request)

        assert processed.request == mock_request
        assert processed.visible is True
        assert processed is not menu  # Should be a copy

    def test_process_with_check_function(self, mock_request):
        """Test processing with custom check function."""

        def check_func(request, **kwargs):
            return request.path == "/test/"

        menu = BaseMenu(name="test", check=check_func, template_name="menu/base.html")

        processed = menu.process(mock_request)

        assert processed.visible is True  # mock_request.path is "/test/"

    def test_process_with_failing_check(self, mock_request):
        """Test processing with failing check."""

        def check_func(request, **kwargs):
            return False

        menu = BaseMenu(name="test", check=check_func, template_name="menu/base.html")

        processed = menu.process(mock_request)

        assert processed.visible is False

    def test_check_method(self, mock_request):
        """Test the check method with different check types."""
        # Boolean check
        menu = BaseMenu(name="test", check=True, template_name="menu/base.html")
        assert menu.check(mock_request) is True

        menu = BaseMenu(name="test", check=False, template_name="menu/base.html")
        assert menu.check(mock_request) is False

        # Callable check
        def custom_check(request, **kwargs):
            return request.path == "/test/"

        menu = BaseMenu(name="test", check=custom_check, template_name="menu/base.html")
        assert menu.check(mock_request) is True

    def test_match_url_no_url(self, mock_request):
        """Test URL matching when no URL is set."""
        menu = BaseMenu(name="test", template_name="menu/base.html")
        menu.request = mock_request

        assert menu.match_url() is False
        assert menu.selected is False

    def test_match_url_with_matching_url(self, mock_request):
        """Test URL matching with matching URL."""
        menu = BaseMenu(name="test", template_name="menu/base.html")
        menu.url = "/test/"
        menu.request = mock_request

        assert menu.match_url() is True
        assert menu.selected is True

    def test_match_url_with_non_matching_url(self, mock_request):
        """Test URL matching with non-matching URL."""
        menu = BaseMenu(name="test", template_name="menu/base.html")
        menu.url = "/other/"
        menu.request = mock_request

        assert menu.match_url() is False
        assert menu.selected is False

    def test_copy(self):
        """Test deep copying of menu."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child = BaseMenu(name="child", template_name="menu/base.html")
        parent.append(child)

        copied = parent.copy()

        assert copied is not parent
        assert copied.name == parent.name
        assert len(copied.children) == len(parent.children)
        assert copied.children[0] is not child  # Deep copy
        assert copied.children[0].name == child.name


class TestMenuLink:
    """Test the MenuLink class functionality."""

    def test_initialization_with_url(self):
        """Test MenuLink initialization with URL."""
        item = MenuLink(name="test", url="/test/")

        assert item.name == "test"
        assert item._url == "/test/"
        assert item.view_name == ""
        assert item.params == {}
        assert item.template_name == "menu/item.html"

    def test_initialization_with_view_name(self):
        """Test MenuLink initialization with view name."""
        item = MenuLink(name="test", view_name="admin:index")

        assert item.name == "test"
        assert item.view_name == "admin:index"
        assert item._url == ""
        assert item.params == {}

    def test_initialization_with_params(self):
        """Test MenuLink initialization with parameters."""
        params = {"id": 1, "slug": "test"}
        item = MenuLink(name="test", url="/test/", params=params)

        assert item.params == params

    def test_initialization_without_url_or_view(self):
        """Test MenuLink initialization fails without URL or view name."""
        with pytest.raises(
            ValueError, match="Either a url or view_name must be provided"
        ):
            MenuLink(name="test")

    def test_process_with_resolvable_url(self, mock_request):
        """Test processing MenuLink with resolvable URL."""
        item = MenuLink(name="test", url="/test/", check=True)

        processed = item.process(mock_request)

        assert processed.visible is True
        assert processed.url == "/test/"
        assert processed.selected is True  # URL matches request path

    def test_process_with_unresolvable_url(self, mock_request):
        """Test processing MenuLink with unresolvable URL."""
        item = MenuLink(name="test", view_name="nonexistent:view", check=True)

        with patch("flex_menu.menu._should_log_url_failures", return_value=False):
            processed = item.process(mock_request)

        assert processed.visible is False  # Hidden due to unresolvable URL

    def test_process_failing_check(self, mock_request):
        """Test processing MenuLink with failing check."""
        item = MenuLink(name="test", url="/test/", check=False)

        processed = item.process(mock_request)

        assert processed.visible is False
        # URL resolution should be skipped

    def test_resolve_url_with_static_url(self):
        """Test resolving static URL."""
        item = MenuLink(name="test", url="/test/")

        url = item.resolve_url()

        assert url == "/test/"

    def test_resolve_url_with_params(self):
        """Test resolving URL with parameters."""
        item = MenuLink(name="test", url="/test/", params={"id": 1, "type": "test"})

        url = item.resolve_url()

        assert url == "/test/?id=1&type=test"

    def test_resolve_url_with_params_existing_query(self):
        """Test resolving URL with parameters when URL already has query string."""
        item = MenuLink(
            name="test", url="/test/?existing=param", params={"new": "param"}
        )

        url = item.resolve_url()

        assert url == "/test/?existing=param&new=param"

    @patch("flex_menu.menu.reverse")
    def test_resolve_url_with_view_name(self, mock_reverse):
        """Test resolving URL with view name."""
        mock_reverse.return_value = "/resolved/"
        item = MenuLink(name="test", view_name="test:view")

        url = item.resolve_url()

        assert url == "/resolved/"
        mock_reverse.assert_called_once_with("test:view", args=(), kwargs={})

    @patch("flex_menu.menu.reverse")
    def test_resolve_url_with_view_name_and_args(self, mock_reverse):
        """Test resolving URL with view name and arguments."""
        mock_reverse.return_value = "/resolved/1/"
        item = MenuLink(name="test", view_name="test:detail")

        url = item.resolve_url(1)

        assert url == "/resolved/1/"
        mock_reverse.assert_called_once_with("test:detail", args=(1,), kwargs={})

    def test_resolve_url_with_callable_url(self, mock_request):
        """Test resolving URL with callable."""

        def url_func(request, *args, **kwargs):
            return f"/dynamic/{request.path}/"

        item = MenuLink(name="test", url=url_func)
        item.request = mock_request

        url = item.resolve_url()

        assert url == "/dynamic//test//"

    def test_resolve_url_with_failing_callable(self, mock_request):
        """Test resolving URL with failing callable."""

        def failing_url_func(request, *args, **kwargs):
            raise Exception("URL generation failed")

        item = MenuLink(name="test", url=failing_url_func)
        item.request = mock_request

        with patch("flex_menu.menu._should_log_url_failures", return_value=False):
            url = item.resolve_url()

        assert url is None

    def test_url_caching(self):
        """Test URL resolution caching for static URLs."""
        item = MenuLink(name="test", url="/test/")

        # First call
        url1 = item.resolve_url()
        assert url1 == "/test/"
        assert hasattr(item, "_cached_url")
        assert item._cached_url == "/test/"

        # Second call should use cache
        url2 = item.resolve_url()
        assert url2 == "/test/"


class TestMenu:
    """Test the MenuGroup class functionality."""

    def test_initialization(self):
        """Test MenuGroup initialization."""
        menu = MenuGroup(name="test_menu")

        assert menu.name == "test_menu"
        assert menu.template_name == "menu/menu.html"
        # Should be attached to root by default
        # Note: parent might be None if root isn't properly initialized
        if menu.parent:
            assert menu.parent.name == "DjangoFlexMenu"

    def test_initialization_with_parent(self):
        """Test MenuGroup initialization with custom parent."""
        parent = BaseMenu(name="custom_parent", template_name="menu/base.html")
        menu = MenuGroup(name="test_menu", parent=parent)

        assert menu.parent == parent

    def test_process_with_children(self, mock_request):
        """Test processing MenuGroup with children."""
        menu = MenuGroup(name="test_menu", check=True)
        child1 = MenuLink(name="child1", url="/child1/", check=True)
        child2 = MenuLink(name="child2", url="/child2/", check=False)
        menu.extend([child1, child2])

        processed = menu.process(mock_request)

        assert processed.visible is True
        assert hasattr(processed, "_processed_children")
        # Only visible children should be included
        assert len(processed._processed_children) == 1
        assert processed._processed_children[0].name == "child1"

    def test_process_no_visible_children(self, mock_request):
        """Test processing MenuGroup with no visible children."""
        menu = MenuGroup(name="test_menu", check=True)
        child = MenuLink(name="child", view_name="nonexistent:view", check=True)
        menu.append(child)

        with patch("flex_menu.menu._should_log_url_failures", return_value=False):
            processed = menu.process(mock_request)

        assert processed.visible is False  # No visible children

    def test_check_with_visible_children(self, mock_request):
        """Test menu visibility check with visible children."""
        menu = MenuGroup(name="test_menu")
        child = MenuLink(name="child", url="/child/", check=True)
        menu.append(child)

        # Create a processed copy first
        processed = menu.process(mock_request)

        assert processed.check(mock_request) is True

    def test_check_no_children(self, mock_request):
        """Test menu visibility check with no children."""
        menu = MenuGroup(name="test_menu")

        assert menu.check(mock_request) is False

    def test_match_url_with_selected_child(self, mock_request):
        """Test URL matching when child is selected."""
        menu = MenuGroup(name="test_menu")
        child = MenuLink(name="child", url="/test/")  # Matches mock_request.path
        menu.append(child)

        processed = menu.process(mock_request)

        assert processed.match_url() is True

    def test_match_url_no_selected_children(self, mock_request):
        """Test URL matching when no children are selected."""
        menu = MenuGroup(name="test_menu")
        child = MenuLink(name="child", url="/other/")  # Doesn't match mock_request.path
        menu.append(child)

        processed = menu.process(mock_request)

        assert processed.match_url() is False


class TestMenuIntegration:
    """Test integration scenarios with complex menu structures."""

    def test_complex_menu_processing(self, complex_menu_tree, authenticated_request):
        """Test processing a complex menu tree."""
        processed = complex_menu_tree.process(authenticated_request)

        assert processed.visible is True
        assert hasattr(processed, "_processed_children")

        # Check that all main sections are processed
        child_names = [child.name for child in processed._processed_children]
        assert "home" in child_names
        assert "about" in child_names
        assert "products" in child_names

    def test_nested_menu_url_matching(self, mock_request, request_factory):
        """Test URL matching in nested menu structures."""
        # Create request for specific product page
        request = request_factory.get("/products/1/")

        menu = MenuGroup(name="main")
        products_menu = MenuGroup(name="products")
        product1 = MenuLink(name="product1", url="/products/1/")
        product2 = MenuLink(name="product2", url="/products/2/")

        menu.append(products_menu)
        products_menu.extend([product1, product2])

        processed = menu.process(request)
        processed_products = processed._processed_children[0]
        processed_product1 = processed_products._processed_children[0]

        assert processed_product1.selected is True
        assert processed_products.match_url() is True
        assert processed.match_url() is True

    def test_menu_with_mixed_visibility(self, mock_request):
        """Test menu with children having different visibility rules."""
        menu = MenuGroup(name="mixed")

        always_visible = MenuLink(name="always", url="/always/", check=True)
        never_visible = MenuLink(name="never", url="/never/", check=False)
        conditionally_visible = MenuLink(
            name="conditional",
            url="/conditional/",
            check=lambda req, **kw: req.path == "/test/",
        )

        menu.extend([always_visible, never_visible, conditionally_visible])

        processed = menu.process(mock_request)

        visible_names = [child.name for child in processed._processed_children]
        assert "always" in visible_names
        assert "conditional" in visible_names  # Request path matches
        assert "never" not in visible_names


class TestCoverageGaps:
    """Tests to address specific code coverage gaps."""

    def test_should_log_url_failures_function(self):
        """Test the _should_log_url_failures function."""
        from django.test import override_settings

        from flex_menu.menu import _should_log_url_failures

        # Test with explicit setting
        with override_settings(FLEX_MENU_LOG_URL_FAILURES=True, DEBUG=False):
            assert _should_log_url_failures() is True

    def test_validate_child_with_invalid_type(self):
        """Test _validate_child with non-BaseMenu object."""
        menu = BaseMenu(name="test", template_name="menu/base.html")

        # Test with invalid child type
        with pytest.raises(TypeError, match="Child must be a BaseMenu instance"):
            menu._validate_child("not a menu")  # type: ignore

    def test_get_with_empty_name(self):
        """Test get method with empty name."""
        menu = BaseMenu(name="test", template_name="menu/base.html")
        child = BaseMenu(name="child", template_name="menu/base.html")
        menu.append(child)

        # Test with empty string
        assert menu.get("") is None

    def test_url_resolution_logging(self):
        """Test URL resolution failure logging."""
        from django.test import override_settings

        item = MenuLink(name="test", view_name="nonexistent:view")

        # Test with logging enabled
        with override_settings(FLEX_MENU_LOG_URL_FAILURES=True):
            with patch("flex_menu.menu.logging.getLogger") as mock_get_logger:
                from unittest.mock import Mock

                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                url = item.resolve_url()

                assert url is None
                mock_logger.warning.assert_called()

    def test_static_url_caching(self):
        """Test URL caching for static URLs."""
        item = MenuLink(name="test", url="/test/")

        # First call should cache the result
        url1 = item.resolve_url()
        assert url1 == "/test/"
        assert hasattr(item, "_cached_url")
        assert item._cached_url == "/test/"

    def test_menu_match_url_without_request(self):
        """Test MenuGroup.match_url when request is not set."""
        menu = MenuGroup(name="test")
        child = MenuLink(name="child", url="/test/")
        menu.append(child)

        # Without request, should return False
        assert menu.match_url() is False


class TestRenderMethods:
    """Test the new render methods for MenuGroup and MenuLink classes."""

    def test_base_menu_render_visible(self, mock_request):
        """Test BaseMenu.render when menu is visible."""
        menu = BaseMenu(name="test", check=True, template_name="menu/base.html")
        menu.request = mock_request
        menu.visible = True

        with patch(
            "flex_menu.menu.render_to_string", return_value="<div>test</div>"
        ) as mock_render:
            result = menu.render()
            assert result == "<div>test</div>"
            mock_render.assert_called_once()

    def test_base_menu_render_not_visible(self, mock_request):
        """Test BaseMenu.render when menu is not visible."""
        menu = BaseMenu(name="test", check=False, template_name="menu/base.html")
        menu.request = mock_request
        menu.visible = False

        result = menu.render()
        assert result == ""

    def test_base_menu_render_with_extra_kwargs(self, mock_request):
        """Test BaseMenu.render with additional kwargs."""
        menu = BaseMenu(name="test", check=True, template_name="menu/base.html")
        menu.request = mock_request
        menu.visible = True

        with patch(
            "flex_menu.menu.render_to_string", return_value="<div>test</div>"
        ) as mock_render:
            result = menu.render(custom_var="test_value")
            assert result == "<div>test</div>"
            mock_render.assert_called_once()
            # Check that get_context_data was called with kwargs
            args, kwargs = mock_render.call_args
            context = args[1]
            assert "custom_var" in context

    def test_menu_render_with_children(self, mock_request):
        """Test MenuGroup template receives children for recursive rendering."""
        menu = MenuGroup(name="parent")
        child1 = MenuLink(name="child1", url="/child1/")
        child2 = MenuLink(name="child2", url="/child2/")

        menu.append(child1)
        menu.append(child2)

        # Process the menu to get visible children
        processed = menu.process(mock_request)
        processed.visible = True

        with patch(
            "flex_menu.menu.render_to_string",
            return_value="<nav>rendered</nav>",
        ) as mock_render:
            result = processed.render()
            assert result == "<nav>rendered</nav>"

            # Check that children context was provided for template
            args, kwargs = mock_render.call_args
            context = args[1]
            assert "children" in context
            assert "has_visible_children" in context
            assert len(context["children"]) == 2

    def test_menu_render_no_visible_children(self, mock_request):
        """Test MenuGroup.render with no visible children."""
        menu = MenuGroup(name="parent")
        menu.request = mock_request
        menu.visible = True
        menu._processed_children = []  # No visible children

        with patch(
            "flex_menu.menu.render_to_string",
            return_value="<nav>empty</nav>",
        ) as mock_render:
            result = menu.render()
            assert result == "<nav>empty</nav>"

            # Check context still contains empty children
            args, kwargs = mock_render.call_args
            context = args[1]
            assert "children" in context
            assert "has_visible_children" in context
            assert len(context["children"]) == 0
            assert context["has_visible_children"] is False


class TestAdditionalCoverage:
    """Additional tests for edge cases and improved coverage."""

    def test_insert_after_fallback_without_move_after(self):
        """Test insert_after fallback when child doesn't have _move_after method."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child1 = BaseMenu(name="child1", template_name="menu/base.html")

        parent.append(child1)

        # Create a mock child without _move_after method
        new_child = BaseMenu(name="new_child", template_name="menu/base.html")
        if hasattr(new_child, "_move_after"):
            delattr(new_child, "_move_after")

        # This should use the fallback implementation
        parent.insert_after(new_child, "child1")

        assert len(parent.children) == 2
        assert list(parent.children)[1].name == "new_child"

    def test_url_resolution_caching_failure(self):
        """Test that failed URL resolution is cached."""
        from django.urls.exceptions import NoReverseMatch

        item = MenuLink(name="test", view_name="nonexistent:view")

        # First call should try to resolve and cache failure
        url1 = item.resolve_url()
        assert url1 is None
        assert hasattr(item, "_cached_url")
        assert item._cached_url is None

        # Second call should use cached failure
        with patch("django.urls.reverse", side_effect=NoReverseMatch) as mock_reverse:
            url2 = item.resolve_url()
            assert url2 is None
            # reverse should not be called again due to caching
            mock_reverse.assert_not_called()

    def test_callable_url_exception_logging(self, mock_request):
        """Test logging when callable URL raises exception."""
        from unittest.mock import Mock

        from django.test import override_settings

        def failing_url_func(request):
            raise ValueError("URL function failed")

        # Create item with callable URL
        item = MenuLink(name="test", url="dummy")  # Provide dummy URL to satisfy validation
        item._url = failing_url_func  # type: ignore # Set callable URL directly
        item.request = mock_request

        # Test with logging enabled
        with override_settings(FLEX_MENU_LOG_URL_FAILURES=True):
            with patch("flex_menu.menu.logging.getLogger") as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                url = item.resolve_url()

                assert url is None
                mock_get_logger.assert_called_once_with("flex_menu.menu")
                mock_logger.warning.assert_called_once()
                assert (
                    "Error calling URL function" in mock_logger.warning.call_args[0][0]
                )

    def test_static_url_caching_with_params(self):
        """Test URL caching behavior with static URLs and parameters."""
        item = MenuLink(name="test", url="/test/", params={"id": "123"})

        # First call should cache the result
        url1 = item.resolve_url()
        expected_url = "/test/?id=123"
        assert url1 == expected_url
        assert hasattr(item, "_cached_url")
        assert item._cached_url == expected_url

        # Second call should use cache
        url2 = item.resolve_url()
        assert url2 == expected_url

    def test_static_url_caching_without_params(self):
        """Test URL caching behavior with static URLs without parameters."""
        item = MenuLink(name="test", url="/simple/")

        # First call should cache the result
        url1 = item.resolve_url()
        assert url1 == "/simple/"
        assert hasattr(item, "_cached_url")
        assert item._cached_url == "/simple/"

        # Second call should use cache
        url2 = item.resolve_url()
        assert url2 == "/simple/"

    def test_menu_match_url_with_request_but_no_match(self, mock_request):
        """Test MenuGroup.match_url with request but no matching children."""
        menu = MenuGroup(name="test")
        child = MenuLink(name="child", url="/test/")
        menu.append(child)

        # Set up request with different path
        mock_request.path = "/different/"
        menu.request = mock_request

        # Mock child.match_url to return False
        with patch.object(child, "match_url", return_value=False):
            assert menu.match_url() is False

    def test_url_resolution_with_args_and_kwargs(self):
        """Test URL resolution with arguments and keyword arguments (no caching)."""
        item = MenuLink(name="test", url="/test/")

        # Call with args/kwargs should not cache
        url = item.resolve_url("arg1", kwarg1="value1")
        assert url == "/test/"
        # Should not cache when args/kwargs are provided
        assert not hasattr(item, "_cached_url")

    def test_resolve_url_return_after_static_url_processing(self):
        """Test that resolve_url properly returns after processing static URLs."""
        # Test simple static URL
        item1 = MenuLink(name="test1", url="/static/")
        result1 = item1.resolve_url()
        assert result1 == "/static/"

        # Test static URL with params
        item2 = MenuLink(name="test2", url="/static/", params={"q": "search"})
        result2 = item2.resolve_url()
        assert result2 == "/static/?q=search"

        # Test static URL with existing query string
        item3 = MenuLink(name="test3", url="/static/?existing=1", params={"new": "2"})
        result3 = item3.resolve_url()
        assert result3 == "/static/?existing=1&new=2"

    def test_should_log_url_failures_debug_fallback(self):
        """Test _should_log_url_failures falls back to DEBUG when FLEX_MENU_LOG_URL_FAILURES not set."""
        from flex_menu.menu import _should_log_url_failures, settings

        # Use patch to simulate getattr behavior when FLEX_MENU_LOG_URL_FAILURES is not set
        # Patch getattr to return DEBUG value when FLEX_MENU_LOG_URL_FAILURES is requested
        with patch.object(settings, "DEBUG", True):
            with patch("flex_menu.menu.getattr") as mock_getattr:
                # Configure getattr to return the DEBUG value (True) when called with the default
                mock_getattr.return_value = True
                result = _should_log_url_failures()
                assert result is True
                # Verify getattr was called with the correct arguments
                mock_getattr.assert_called_once_with(
                    settings, "FLEX_MENU_LOG_URL_FAILURES", True
                )
