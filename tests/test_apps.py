"""
Tests for django-flex-menus Django app configuration.
"""

import types
from unittest.mock import Mock, patch

from flex_menu import root
from flex_menu.apps import FlexMenuConfig
from flex_menu.menu import BaseMenu, MenuGroup


def create_mock_module(name):
    """Create a proper mock module that Django can work with."""
    module = types.ModuleType(name)
    module.__file__ = f"/{name.replace('.', '/')}.py"
    module.__path__ = [f"/{name.replace('.', '/')}/"]
    return module


class TestFlexMenuAppConfig:
    """Test the FlexMenuConfig app configuration."""

    def test_autodiscover_functionality(self):
        """Test that autodiscover actually works for menu modules."""
        # Create a mock module with menu definitions
        mock_module = Mock()
        mock_module.test_menu = Mock()

        with patch("flex_menu.apps.autodiscover_modules") as mock_autodiscover:
            # Simulate autodiscover finding our mock module
            mock_autodiscover.return_value = [mock_module]

            # Create a proper mock module for the app
            app_module = create_mock_module("flex_menu")
            config = FlexMenuConfig("flex_menu", app_module)
            config.ready()

            mock_autodiscover.assert_called_once_with("menus")

    def test_app_ready_signal(self):
        """Test that the app ready signal works correctly."""
        # This test verifies the autodiscover mechanism works in practice
        with patch("flex_menu.apps.autodiscover_modules") as mock_autodiscover:
            # Import and trigger the ready method
            from flex_menu.apps import FlexMenuConfig

            app_module = create_mock_module("flex_menu")
            config = FlexMenuConfig("flex_menu", app_module)
            config.ready()

            # Verify autodiscover was called
            mock_autodiscover.assert_called_with("menus")


class TestMenuModuleDiscovery:
    """Test the menu module discovery functionality."""

    def test_discover_menus_module(self):
        """Test discovering a menus.py module."""
        # Create a mock menus module
        mock_menus_module = Mock()
        mock_menus_module.__name__ = "testapp.menus"

        # Mock menu items in the module
        from flex_menu.menu import MenuGroup, MenuLink

        mock_menu = MenuGroup(name="discovered_menu")
        mock_item = MenuLink(name="discovered_item", url="/discovered/")
        mock_menu.append(mock_item)

        mock_menus_module.main_menu = mock_menu

        with patch("flex_menu.apps.autodiscover_modules") as mock_autodiscover:
            # Simulate finding the menus module
            def side_effect(module_name):
                if module_name == "menus":
                    # Simulate the module being imported and processed
                    return [mock_menus_module]
                return []

            mock_autodiscover.side_effect = side_effect

            app_module = create_mock_module("flex_menu")
            config = FlexMenuConfig("flex_menu", app_module)
            config.ready()

            mock_autodiscover.assert_called_once_with("menus")

    def test_no_menus_modules_found(self):
        """Test behavior when no menus modules are found."""
        with patch("flex_menu.apps.autodiscover_modules") as mock_autodiscover:
            # Return empty list (no modules found)
            mock_autodiscover.return_value = []

            app_module = create_mock_module("flex_menu")
            config = FlexMenuConfig("flex_menu", app_module)

            # Should not raise any errors
            config.ready()

            mock_autodiscover.assert_called_once_with("menus")


class TestFlexMenuGlobalRoot:
    """Test the global root menu object."""

    def test_root_menu_exists(self):
        """Test that the global root menu is available."""
        assert isinstance(root, BaseMenu)
        assert root.name == "DjangoFlexMenu"

    def test_root_menu_modification(self):
        """Test that the root menu can be modified."""
        test_menu = MenuGroup(name="test_root_menu")
        root.append(test_menu)

        assert test_menu in root.children
        assert root.get("test_root_menu") == test_menu

    def test_root_menu_persistence(self):
        """Test that root menu modifications persist across imports."""
        persistent_menu = MenuGroup(name="persistent")
        root.append(persistent_menu)

        from flex_menu import root as root2

        assert root is root2
        assert root2.get("persistent") == persistent_menu
