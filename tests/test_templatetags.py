"""
Tests for django-flex-menus templatetags.
"""

from unittest.mock import Mock, patch

import pytest
from django.template import Context, Template

from flex_menu.menu import BaseMenu, MenuGroup, MenuLink
from flex_menu.templatetags.flex_menu import process_menu, render_menu


class TestProcessMenuTag:
    """Test the process_menu template tag."""

    def test_process_menu_with_menu_object(self, mock_request):
        """Test process_menu with a menu object."""
        menu = BaseMenu(name="test", check=True, template_name="menu/base.html")
        context = {"request": mock_request}

        processed = process_menu(context, menu)

        assert processed is not None
        assert processed.request == mock_request
        assert processed.visible is True

    def test_process_menu_with_menu_name(self, mock_request):
        """Test process_menu with a menu name string."""
        from flex_menu import root

        # Add a menu to root
        test_menu = BaseMenu(name="test_menu", check=True, template_name="menu/base.html")
        root.append(test_menu)

        context = {"request": mock_request}

        processed = process_menu(context, "test_menu")

        assert processed is not None
        assert processed.name == "test_menu"
        assert processed.visible is True

        # Clean up
        test_menu.parent = None

    def test_process_menu_with_nonexistent_name(self, mock_request):
        """Test process_menu with nonexistent menu name."""
        context = {"request": mock_request}
        import pytest

        with pytest.raises(Exception) as excinfo:
            process_menu(context, "nonexistent_menu")
        # Check for TemplateSyntaxError and message content
        assert excinfo.type.__name__ == "TemplateSyntaxError"
        assert "nonexistent_menu" in str(excinfo.value)
        assert "python manage.py render_menu" in str(excinfo.value)

    def test_process_menu_with_kwargs(self, mock_request):
        """Test process_menu passing additional kwargs."""

        def custom_check(request, custom_param=None, **kwargs):
            return custom_param == "test_value"

        menu = BaseMenu(name="test", check=custom_check, template_name="menu/base.html")
        context = {"request": mock_request}

        processed = process_menu(context, menu, custom_param="test_value")

        assert processed.visible is True

    def test_process_menu_none_menu(self, mock_request):
        """Test process_menu with None menu."""
        context = {"request": mock_request}

        processed = process_menu(context, None)

        assert processed is None


class TestRenderMenuTag:
    """Test the render_menu template tag."""

    def test_render_menu_with_visible_menu(self, mock_request):
        """Test render_menu with visible menu."""
        menu = BaseMenu(name="test", check=True, template_name="menu/base.html")
        context = {"request": mock_request}

        with patch("flex_menu.menu.render_to_string") as mock_render:
            mock_render.return_value = "<div>Test MenuGroup</div>"

            result = render_menu(context, menu)

            assert result == "<div>Test MenuGroup</div>"
            # Check that the menu's render method was called
            mock_render.assert_called_once()

    def test_render_menu_uses_menu_template(self, mock_request):
        """Test render_menu uses the menu's configured template."""
        menu = BaseMenu(name="test", check=True, template_name="custom/template.html")
        context = {"request": mock_request}

        with patch("flex_menu.menu.render_to_string") as mock_render:
            mock_render.return_value = "<div>MenuGroup Template</div>"

            result = render_menu(context, menu)

            assert result == "<div>MenuGroup Template</div>"
            # Check that the menu's render method was called
            mock_render.assert_called_once()

    def test_render_menu_with_invisible_menu(self, mock_request):
        """Test render_menu with invisible menu."""
        menu = BaseMenu(name="test", check=False, template_name="menu/base.html")
        context = {"request": mock_request}

        result = render_menu(context, menu)

        assert result == ""

    def test_render_menu_with_none_menu(self, mock_request):
        """Test render_menu with None menu."""
        context = {"request": mock_request}

        result = render_menu(context, None)

        assert result == ""

    def test_render_menu_with_menu_name(self, mock_request):
        """Test render_menu with menu name string."""
        from flex_menu import root

        # Add a menu to root
        test_menu = BaseMenu(name="test_menu", check=True, template_name="menu/base.html")
        root.append(test_menu)

        context = {"request": mock_request}

        # Mock the menu's render method after processing
        with patch("flex_menu.menu.render_to_string") as mock_render:
            mock_render.return_value = "<div>Named MenuGroup</div>"

            result = render_menu(context, "test_menu")

            assert result == "<div>Named MenuGroup</div>"

        # Clean up
        test_menu.parent = None

    def test_render_menu_with_kwargs(self, mock_request):
        """Test render_menu with additional processing kwargs."""

        def custom_check(request, test_param=None, **kwargs):
            return test_param == "visible"

        menu = BaseMenu(name="test", check=custom_check, template_name="menu/base.html")
        context = {"request": mock_request}

        # Mock render_to_string to control the output
        with patch("flex_menu.menu.render_to_string") as mock_render_to_string:
            mock_render_to_string.return_value = "<div>Conditional MenuGroup</div>"

            result = render_menu(context, menu, test_param="visible")

            assert result == "<div>Conditional MenuGroup</div>"


class TestTemplateTagIntegration:
    """Test templatetags in actual Django templates."""

    def test_process_menu_in_template(self, mock_request):
        """Test using process_menu tag in a Django template."""
        from flex_menu import root

        # Create a test menu
        test_menu = MenuLink(name="test_menu", url="/test/", check=True)
        root.append(test_menu)

        template_string = """
        {% load flex_menu %}
        {% process_menu menu_name as processed_menu %}
        {% if processed_menu %}
        <div>{{ processed_menu.name }}: {{ processed_menu.visible }}</div>
        {% endif %}
        """

        template = Template(template_string)
        context = Context({"request": mock_request, "menu_name": "test_menu"})

        rendered = template.render(context)

        assert "test_menu: True" in rendered

        # Clean up
        test_menu.parent = None

    def test_render_menu_in_template(self, mock_request):
        """Test using render_menu tag in a Django template."""
        from flex_menu import root

        # Create a test menu with simple template
        test_menu = BaseMenu(name="test_menu", check=True, template_name="menu/base.html")
        test_menu.template_name = "menu/simple.html"
        root.append(test_menu)

        template_string = """
        {% load flex_menu %}
        {% render_menu menu_name %}
        """

        with patch("flex_menu.menu.render_to_string") as mock_render:
            mock_render.return_value = "<nav>Test MenuGroup</nav>"

            template = Template(template_string)
            context = Context({"request": mock_request, "menu_name": "test_menu"})

            rendered = template.render(context)

            # The HTML should not be escaped since menu.render() uses mark_safe()
            assert "<nav>Test MenuGroup</nav>" in rendered

        # Clean up
        test_menu.parent = None

    def test_complex_menu_rendering(self, mock_request, complex_menu_tree):
        """Test rendering a complex menu structure."""
        from flex_menu import root

        # Attach complex menu to root for testing
        root.append(complex_menu_tree)

        template_string = """
        {% load flex_menu %}
        {% render_menu menu_name %}
        """

        with patch("flex_menu.menu.render_to_string") as mock_render:
            mock_render.return_value = "<nav><ul><li>Home</li><li>About</li></ul></nav>"

            template = Template(template_string)
            context = Context(
                {
                    "request": mock_request,
                    "menu_name": "test_menu",  # complex_menu_tree has name "test_menu"
                }
            )

            rendered = template.render(context)

            assert "<nav>" in rendered
            assert "Home" in rendered
            assert "About" in rendered

        # Clean up
        complex_menu_tree.parent = None

    def test_menu_with_authentication_checks(self, mock_request, authenticated_request):
        """Test menu rendering with authentication-based visibility."""
        from flex_menu import root
        from flex_menu.checks import user_is_authenticated

        # Create menus with different visibility rules
        public_menu = MenuLink(name="public", url="/public/", check=True)
        auth_menu = MenuLink(
            name="auth_only", url="/private/", check=user_is_authenticated
        )

        main_menu = MenuGroup(name="main_menu")
        main_menu.extend([public_menu, auth_menu])
        root.append(main_menu)

        template_string = """
        {% load flex_menu %}
        {% process_menu "main_menu" as menu %}
        {% if menu %}
        <nav>
            {% for item in menu.processed_children %}
            <a href="{{ item.url }}">{{ item.name }}</a>
            {% endfor %}
        </nav>
        {% endif %}
        """

        # Test with anonymous user
        template = Template(template_string)
        anon_context = Context({"request": mock_request})
        mock_request.user = Mock()
        mock_request.user.is_authenticated = False

        anon_rendered = template.render(anon_context)
        assert "public" in anon_rendered
        assert "auth_only" not in anon_rendered

        # Test with authenticated user
        auth_context = Context({"request": authenticated_request})
        auth_rendered = template.render(auth_context)
        assert "public" in auth_rendered
        assert "auth_only" in auth_rendered

        # Clean up
        main_menu.parent = None


class TestTemplateTagErrorHandling:
    """Test error handling in templatetags."""

    def test_process_menu_missing_request(self):
        """Test process_menu without request in context."""
        menu = BaseMenu(name="test", check=True, template_name="menu/base.html")
        context = {}  # No request

        with pytest.raises(KeyError):
            process_menu(context, menu)

    def test_render_menu_missing_request(self):
        """Test render_menu without request in context."""
        menu = BaseMenu(name="test", check=True, template_name="menu/base.html")
        context = {}  # No request

        with pytest.raises(KeyError):
            render_menu(context, menu)

    def test_process_menu_with_exception_in_check(self, mock_request):
        """Test process_menu when check function raises exception."""

        def failing_check(request, **kwargs):
            raise Exception("Check failed")

        menu = BaseMenu(name="test", check=failing_check, template_name="menu/base.html")
        context = {"request": mock_request}

        # Should handle exception gracefully
        with pytest.raises(Exception):
            process_menu(context, menu)

    def test_render_menu_template_not_found(self, mock_request):
        """Test render_menu when template doesn't exist."""
        menu = BaseMenu(name="test", check=True, template_name="nonexistent.html")
        context = {"request": mock_request}

        with patch("flex_menu.menu.render_to_string") as mock_render:
            mock_render.side_effect = Exception("Template not found")

            with pytest.raises(Exception):
                render_menu(context, menu)
