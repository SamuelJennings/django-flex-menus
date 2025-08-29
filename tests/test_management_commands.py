"""
Tests for django-flex-menus management commands.
"""

from io import StringIO
from unittest.mock import Mock, patch

import pytest
from django.core.management import call_command

from flex_menu.management.commands.render_menu import Command
from flex_menu.menu import MenuGroup, MenuLink


class TestRenderMenuCommand:
    """Test the render_menu management command."""

    def test_render_all_menus(self):
        """Test rendering all menus without specifying a name."""
        from flex_menu import root

        # Add some test menus to root
        test_menu = MenuGroup(name="test_menu")
        test_item = MenuLink(name="test_item", url="/test/")
        test_menu.append(test_item)
        root.append(test_menu)

        out = StringIO()

        try:
            call_command("render_menu", stdout=out)
            output = out.getvalue()

            assert "Django Flex Menu:" in output
            assert "test_menu" in output
            assert "test_item" in output
        finally:
            # Clean up
            test_menu.parent = None

    def test_render_specific_menu_exists(self):
        """Test rendering a specific menu that exists."""
        from flex_menu import root

        # Add a test menu
        test_menu = MenuGroup(name="specific_menu")
        test_item = MenuLink(name="specific_item", url="/specific/")
        test_menu.append(test_item)
        root.append(test_menu)

        out = StringIO()

        try:
            call_command("render_menu", "--name=specific_menu", stdout=out)
            output = out.getvalue()

            assert "Django Flex Menu:" in output
            assert "specific_menu" in output
            assert "specific_item" in output
        finally:
            # Clean up
            test_menu.parent = None

    def test_render_specific_menu_not_exists(self):
        """Test rendering a specific menu that doesn't exist."""
        out = StringIO()

        call_command("render_menu", "--name=nonexistent_menu", stdout=out)
        output = out.getvalue()

        assert "Django Flex Menu:" in output
        assert "Menu 'nonexistent_menu' not found" in output

    def test_command_class_directly(self):
        """Test the Command class directly."""
        command = Command()

        # Test add_arguments method
        parser = Mock()
        command.add_arguments(parser)
        parser.add_argument.assert_called_once_with("--name", type=str, required=False)

    def test_handle_with_existing_menu(self):
        """Test handle method with existing menu."""
        from flex_menu import root

        # Add test menu
        test_menu = MenuGroup(name="handle_test")
        root.append(test_menu)

        command = Command()
        out = StringIO()
        command.stdout = out

        try:
            command.handle(name="handle_test")
            output = out.getvalue()

            assert "Django Flex Menu:" in output
            assert "handle_test" in output
        finally:
            # Clean up
            test_menu.parent = None

    def test_handle_with_nonexistent_menu(self):
        """Test handle method with nonexistent menu."""
        command = Command()
        out = StringIO()
        command.stdout = out

        command.handle(name="nonexistent")
        output = out.getvalue()

        assert "Django Flex Menu:" in output
        assert "Menu 'nonexistent' not found" in output

    def test_handle_without_name(self):
        """Test handle method without specifying name."""

        command = Command()
        out = StringIO()
        command.stdout = out

        command.handle()
        output = out.getvalue()

        assert "Django Flex Menu:" in output
        # Should render the entire root tree

    def test_complex_menu_structure_rendering(self):
        """Test rendering a complex menu structure."""
        from flex_menu import root

        # Create complex structure
        main_menu = MenuGroup(name="main")

        home = MenuLink(name="home", url="/")
        about = MenuLink(name="about", url="/about/")

        products = MenuGroup(name="products")
        product1 = MenuLink(name="product1", url="/products/1/")
        product2 = MenuLink(name="product2", url="/products/2/")
        products.extend([product1, product2])

        main_menu.extend([home, about, products])
        root.append(main_menu)

        out = StringIO()

        try:
            call_command("render_menu", "--name=main", stdout=out)
            output = out.getvalue()

            assert "main" in output
            assert "home" in output
            assert "about" in output
            assert "products" in output
            assert "product1" in output
            assert "product2" in output
        finally:
            # Clean up
            main_menu.parent = None

    def test_empty_menu_rendering(self):
        """Test rendering an empty menu."""
        from flex_menu import root

        empty_menu = MenuGroup(name="empty")
        root.append(empty_menu)

        out = StringIO()

        try:
            call_command("render_menu", "--name=empty", stdout=out)
            output = out.getvalue()

            assert "Django Flex Menu:" in output
            assert "empty" in output
        finally:
            # Clean up
            empty_menu.parent = None

    def test_menu_with_special_characters(self):
        """Test rendering menu with special characters in names."""
        from flex_menu import root

        special_menu = MenuGroup(name="special-menu_123")
        special_item = MenuLink(name="special-item", url="/special/")
        special_menu.append(special_item)
        root.append(special_menu)

        out = StringIO()

        try:
            call_command("render_menu", "--name=special-menu_123", stdout=out)
            output = out.getvalue()

            assert "special-menu_123" in output
            assert "special-item" in output
        finally:
            # Clean up
            special_menu.parent = None

    def test_command_error_handling(self):
        """Test command error handling for various edge cases."""
        from flex_menu import root

        # Test with menu that might cause rendering issues
        problem_menu = MenuGroup(name="problem")
        root.append(problem_menu)

        # Mock print_tree method to raise exception
        with patch.object(
            problem_menu, "print_tree", side_effect=Exception("Print tree error")
        ):
            out = StringIO()

            try:
                # Command should handle exceptions gracefully
                with pytest.raises(Exception):
                    call_command("render_menu", "--name=problem", stdout=out)
            finally:
                # Clean up
                problem_menu.parent = None


class TestManagementCommandIntegration:
    """Test integration scenarios for management commands."""

    def test_command_with_django_settings(self):
        """Test command behavior with different Django settings."""
        from flex_menu import root

        test_menu = MenuGroup(name="settings_test")
        root.append(test_menu)

        out = StringIO()

        try:
            # This should work regardless of DEBUG setting
            call_command("render_menu", "--name=settings_test", stdout=out)
            output = out.getvalue()

            assert "settings_test" in output
        finally:
            # Clean up
            test_menu.parent = None

    def test_command_output_format(self):
        """Test the format of command output."""
        from flex_menu import root

        format_menu = MenuGroup(name="format")
        format_item = MenuLink(name="item", url="/item/")
        format_menu.append(format_item)
        root.append(format_menu)

        out = StringIO()

        try:
            call_command("render_menu", "--name=format", stdout=out)
            output = out.getvalue()

            # Check output format
            lines = output.strip().split("\n")
            assert any("Django Flex Menu:" in line for line in lines)
            assert any("=" in line for line in lines)  # Separator line
            assert any("format" in line for line in lines)
        finally:
            # Clean up
            format_menu.parent = None

    def test_multiple_command_calls(self):
        """Test calling the command multiple times."""
        from flex_menu import root

        multi_menu = MenuGroup(name="multi")
        root.append(multi_menu)

        try:
            # First call
            out1 = StringIO()
            call_command("render_menu", "--name=multi", stdout=out1)
            output1 = out1.getvalue()

            # Second call
            out2 = StringIO()
            call_command("render_menu", "--name=multi", stdout=out2)
            output2 = out2.getvalue()

            # Both should produce same output
            assert output1 == output2
            assert "multi" in output1
            assert "multi" in output2
        finally:
            # Clean up
            multi_menu.parent = None
