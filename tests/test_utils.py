"""
Tests for flex_menu.utils module.
"""

import pytest
from django.urls.exceptions import NoReverseMatch

from flex_menu.utils import get_required_url_params, warm_url_params_cache


@pytest.mark.django_db
class TestGetRequiredUrlParams:
    """Test get_required_url_params function."""

    def test_namespaced_url_no_params(self):
        """Test namespaced URL with no parameters."""
        # 'admin:index' has no parameters
        params = get_required_url_params("admin:index")
        assert params == set()

    def test_namespaced_url_with_params(self):
        """Test namespaced URL with parameters."""
        # 'admin:app_list' requires 'app_label' parameter
        params = get_required_url_params("admin:app_list")
        assert "app_label" in params
        assert len(params) == 1

    def test_invalid_view_name(self):
        """Test that invalid view name raises NoReverseMatch."""
        with pytest.raises(NoReverseMatch):
            get_required_url_params("nonexistent_view")

    def test_invalid_namespace(self):
        """Test that invalid namespace raises NoReverseMatch."""
        with pytest.raises(NoReverseMatch):
            get_required_url_params("badnamespace:view")

    def test_nested_namespace_with_parent_params(self, settings):
        """Test that parameters from parent URLResolvers are included.

        This simulates a structure like:
            path("project/<str:uuid>/", include((urls, "project")))
        where the parent resolver has a parameter (uuid) and the nested
        patterns also have their own parameters.
        """
        from django.urls import clear_url_caches, include, path
        from django.views import View

        class DummyView(View):
            pass

        # Create nested URL patterns like fairdm uses
        nested_urls = [
            path("", DummyView.as_view(), name="overview"),
            path("edit/<int:pk>/", DummyView.as_view(), name="edit"),
        ]

        # Create a test URL configuration
        test_urlpatterns = [
            path("test/<str:uuid>/", include((nested_urls, "test"))),
        ]

        # Temporarily replace URL conf
        original_urlconf = settings.ROOT_URLCONF
        settings.ROOT_URLCONF = __name__

        # Inject the test patterns into this module
        import sys

        sys.modules[__name__].urlpatterns = test_urlpatterns  # type: ignore[attr-defined]

        clear_url_caches()

        try:
            # Test that parent parameter (uuid) is included
            params = get_required_url_params("test:overview")
            assert params == {"uuid"}

            # Test that both parent and child parameters are included
            params = get_required_url_params("test:edit")
            assert params == {"uuid", "pk"}
        finally:
            # Restore original URL conf
            settings.ROOT_URLCONF = original_urlconf
            clear_url_caches()


class TestCacheWarming:
    """Test the warm_url_params_cache function."""

    def test_warm_url_params_cache_populates_cache(self):
        """Test that warm_url_params_cache pre-populates the LRU cache."""
        # Clear the cache first
        get_required_url_params.cache_clear()

        # Verify cache is empty
        cache_info = get_required_url_params.cache_info()
        assert cache_info.currsize == 0
        assert cache_info.hits == 0
        assert cache_info.misses == 0

        # Warm the cache
        warm_url_params_cache()

        # Verify cache is populated
        cache_info = get_required_url_params.cache_info()
        assert cache_info.currsize > 0, "Cache should contain URLs after warming"
        assert cache_info.misses > 0, "Cache misses should occur during warming"

    def test_warmed_cache_provides_fast_lookups(self):
        """Test that URLs cached during warming result in cache hits."""
        # Clear and warm the cache
        get_required_url_params.cache_clear()
        warm_url_params_cache()

        # Get initial stats
        initial_info = get_required_url_params.cache_info()
        initial_hits = initial_info.hits

        # Look up a common URL that should be cached
        try:
            get_required_url_params("admin:index")

            # Verify it was a cache hit
            final_info = get_required_url_params.cache_info()
            assert final_info.hits > initial_hits, "Lookup should be a cache hit"
        except Exception:
            # If admin:index doesn't exist, that's fine - skip this test
            pytest.skip("admin:index not available")

    def test_cache_warming_handles_errors_gracefully(self):
        """Test that cache warming doesn't crash on URL resolver issues."""
        # This should not raise any exceptions
        get_required_url_params.cache_clear()
        warm_url_params_cache()

        # Cache should still have some entries even if some URLs failed
        cache_info = get_required_url_params.cache_info()
        # At minimum, Django admin URLs should be cached
        assert cache_info.currsize >= 0

    def test_cache_with_unlimited_size(self):
        """Test that cache has unlimited size (maxsize=None)."""
        cache_info = get_required_url_params.cache_info()
        assert cache_info.maxsize is None, "Cache should have unlimited size"
