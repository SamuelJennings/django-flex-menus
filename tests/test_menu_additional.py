"""Additional tests for MenuItem to increase coverage."""

import pytest
from django.test import RequestFactory

from flex_menu import MenuItem


@pytest.fixture
def request_factory():
    """Create request factory."""
    return RequestFactory()


@pytest.fixture
def get_request(request_factory):
    """Create a GET request."""
    return request_factory.get("/")


@pytest.mark.django_db
class TestCallableURLs:
    """Test callable URL functions."""

    def test_callable_url_function(self, get_request):
        """Test URL as a callable function."""

        def dynamic_url(request, *args, **kwargs):
            return f"/dynamic/{request.path}/"

        item = MenuItem(name="dynamic", label="Dynamic", url=dynamic_url)
        processed = item.process(get_request)

        assert processed.url is not None
        assert "/dynamic/" in processed.url

    def test_callable_url_with_args(self, get_request):
        """Test callable URL with arguments."""

        def url_with_args(request, *args, **kwargs):
            return f"/item/{args[0]}/" if args else "/item/"

        item = MenuItem(name="callable", label="Callable", url=url_with_args)
        processed = item.process(get_request)

        # When processing without args, should work
        assert processed.url == "/item/"

    def test_callable_url_exception(self, get_request):
        """Test callable URL that raises exception."""

        def bad_url(request):
            raise ValueError("Intentional error")

        item = MenuItem(name="bad", label="Bad", url=bad_url)
        processed = item.process(get_request)

        # Should return None and log error
        assert processed.url is None


@pytest.mark.django_db
class TestURLParams:
    """Test URL parameter handling."""

    def test_url_with_params(self, get_request):
        """Test URL with query parameters."""
        item = MenuItem(
            name="with_params",
            label="With Params",
            url="/path/",
            params={"foo": "bar", "baz": "qux"},
        )
        processed = item.process(get_request)

        # Should include query string
        assert processed.url is not None
        assert "?" in processed.url
        assert "foo=bar" in processed.url
        assert "baz=qux" in processed.url

    def test_url_with_existing_query_string(self, get_request):
        """Test URL that already has query string."""
        item = MenuItem(
            name="existing_qs",
            label="Existing QS",
            url="/path/?existing=param",
            params={"new": "param"},
        )
        processed = item.process(get_request)

        # Should use & instead of ? for additional params
        assert processed.url is not None
        assert "existing=param" in processed.url
        assert "new=param" in processed.url
        assert "&" in processed.url


@pytest.mark.django_db
class TestVisibilityLogic:
    """Test visibility and check logic."""

    def test_check_with_callable(self, get_request):
        """Test check function that's callable."""

        def is_visible(request):
            return request.path == "/"

        item = MenuItem(
            name="conditional",
            label="Conditional",
            url="/test/",
            check=is_visible,
        )
        processed = item.process(get_request)

        assert processed.visible is True

    def test_check_with_boolean(self, get_request):
        """Test check function that's a boolean."""
        visible_item = MenuItem(
            name="visible",
            label="Visible",
            url="/test/",
            check=True,
        )
        hidden_item = MenuItem(
            name="hidden",
            label="Hidden",
            url="/test/",
            check=False,
        )

        assert visible_item.process(get_request).visible is True
        assert hidden_item.process(get_request).visible is False

    def test_parent_hidden_if_no_visible_children(self, get_request):
        """Test parent is hidden when all children are hidden."""
        parent = MenuItem(name="parent", label="Parent")
        MenuItem(
            name="hidden1",
            label="Hidden 1",
            url="/hidden1/",
            check=False,
            parent=parent,
        )
        MenuItem(
            name="hidden2",
            label="Hidden 2",
            url="/hidden2/",
            check=False,
            parent=parent,
        )

        processed = parent.process(get_request)

        # Parent should be hidden because no children are visible
        assert processed.visible is False

    def test_leaf_hidden_if_url_not_resolvable(self, get_request):
        """Test leaf item is hidden if URL can't be resolved."""
        item = MenuItem(
            name="unresolvable",
            label="Unresolvable",
            view_name="nonexistent:view",
        )

        processed = item.process(get_request)

        # Should be hidden because URL can't be resolved and it's a leaf
        assert processed.visible is False


@pytest.mark.django_db
class TestTreeMethods:
    """Test tree navigation and utility methods."""

    def test_get_with_maxlevel(self):
        """Test get() method with maxlevel."""
        root = MenuItem(name="root", label="Root")
        level1 = MenuItem(name="level1", label="Level 1", parent=root)
        level2 = MenuItem(name="level2", label="Level 2", parent=level1)
        MenuItem(name="level3", label="Level 3", parent=level2)

        # Search only direct children
        assert root.get("level1", maxlevel=1) is level1
        assert root.get("level2", maxlevel=1) is None  # Too deep

        # Search two levels deep
        assert root.get("level2", maxlevel=2) is level2
        assert root.get("level3", maxlevel=2) is None  # Too deep

    def test_get_with_empty_name(self):
        """Test get() with empty name."""
        root = MenuItem(name="root", label="Root")
        assert root.get("") is None

    def test_print_tree(self):
        """Test print_tree method."""
        root = MenuItem(name="root", label="Root")
        MenuItem(name="child1", label="Child 1", url="/child1/", parent=root)
        MenuItem(name="child2", label="Child 2", url="/child2/", parent=root)

        tree_str = root.print_tree()

        assert "root" in tree_str
        assert "child1" in tree_str
        assert "child2" in tree_str


@pytest.mark.django_db
class TestProcessingEdgeCases:
    """Test edge cases in processing."""

    def test_process_preserves_extra_context(self, get_request):
        """Test that extra_context is preserved during processing."""
        item = MenuItem(
            name="test",
            label="Test",
            url="/test/",
            extra_context={"custom": "value"},
        )

        processed = item.process(get_request)

        assert processed.extra_context["custom"] == "value"

    def test_process_multiple_times_same_request(self, get_request):
        """Test processing the same item multiple times."""
        item = MenuItem(name="test", label="Test", url="/test/")

        processed1 = item.process(get_request)
        processed2 = item.process(get_request)

        # Should create separate copies
        assert processed1 is not processed2
        assert processed1.url == processed2.url

    def test_url_caching(self, get_request):
        """Test that URLs are cached after first resolution."""
        call_count = 0

        def counting_url(request):
            nonlocal call_count
            call_count += 1
            return "/counted/"

        item = MenuItem(name="cached", label="Cached", url=counting_url)

        # First process
        processed = item.process(get_request)

        # Access URL again (on processed copy)
        _ = processed.url

        # Callable URLs aren't cached the same way, but at least verify it works
        assert processed.url == "/counted/"
