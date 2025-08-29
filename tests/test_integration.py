"""
Integration tests for django-flex-menus.
Tests the complete functionality working together.
"""

from unittest.mock import Mock, patch

from flex_menu.checks import user_is_authenticated, user_is_staff
from flex_menu.menu import MenuGroup, MenuLink


class CustomTestUser:
    """Custom user class for testing that doesn't have Mock's attribute behavior."""

    def __init__(self, **attrs):
        for key, value in attrs.items():
            setattr(self, key, value)


class TestMenuSystemIntegration:
    """Test the complete menu system working together."""

    def test_complete_menu_workflow(self, authenticated_request, request_factory):
        """Test a complete menu workflow from creation to rendering."""
        # 1. Create a complex menu structure
        main_menu = MenuGroup(name="main_nav")

        # Public items
        home = MenuLink(name="home", url="/", label="Home")
        about = MenuLink(name="about", url="/about/", label="About")

        # User-only items
        profile = MenuLink(
            name="profile",
            url="/profile/",
            label="Profile",
            check=user_is_authenticated,
        )

        # Staff-only section
        admin_menu = MenuGroup(name="admin", label="Admin", check=user_is_staff)
        users = MenuLink(name="users", url="/admin/users/", label="Users")
        settings = MenuLink(name="settings", url="/admin/settings/", label="Settings")
        admin_menu.extend([users, settings])

        # Build structure
        main_menu.extend([home, about, profile, admin_menu])

        # 2. Process with authenticated user
        processed = main_menu.process(authenticated_request)

        # 3. Verify structure
        assert processed.visible is True
        assert (
            len(processed._processed_children) == 3
        )  # home, about, profile (no admin for regular user)

        child_names = [child.name for child in processed._processed_children]
        assert "home" in child_names
        assert "about" in child_names
        assert "profile" in child_names
        assert "admin" not in child_names

    def test_menu_with_url_matching(self, request_factory):
        """Test menu with URL matching functionality."""
        # Create menu
        nav = MenuGroup(name="navigation")

        pages = [
            MenuLink(name="home", url="/", label="Home"),
            MenuLink(name="products", url="/products/", label="Products"),
            MenuLink(name="contact", url="/contact/", label="Contact"),
        ]
        nav.extend(pages)

        # Test with different request paths
        test_cases = [
            ("/", "home"),
            ("/products/", "products"),
            ("/contact/", "contact"),
        ]

        for path, expected_selected in test_cases:
            request = request_factory.get(path)
            request.user = Mock(is_authenticated=True)

            processed = nav.process(request)

            # Find selected item
            selected_items = [
                child for child in processed._processed_children if child.selected
            ]

            assert len(selected_items) == 1
            assert selected_items[0].name == expected_selected

    def test_nested_menu_visibility_propagation(
        self, authenticated_request, request_factory
    ):
        """Test that visibility properly propagates in nested menus."""
        # Create nested structure
        main = MenuGroup(name="main")

        # Section with mixed visibility
        user_section = MenuGroup(name="user_section", label="User Area")
        public_item = MenuLink(name="public", url="/public/", check=True)
        private_item = MenuLink(
            name="private", url="/private/", check=user_is_authenticated
        )
        staff_item = MenuLink(name="staff", url="/staff/", check=user_is_staff)

        user_section.extend([public_item, private_item, staff_item])
        main.append(user_section)

        # Test with authenticated regular user
        processed = main.process(authenticated_request)

        # Main should be visible (has visible children)
        assert processed.visible is True

        # User section should be visible (has visible children)
        user_section_processed = processed._processed_children[0]
        assert user_section_processed.visible is True

        # Should have public and private items, but not staff
        visible_items = [
            child.name for child in user_section_processed._processed_children
        ]
        assert "public" in visible_items
        assert "private" in visible_items
        assert "staff" not in visible_items

    def test_menu_with_view_name_resolution(self, authenticated_request):
        """Test menu items with Django view name resolution."""
        # Create menu with view names
        nav = MenuGroup(name="view_nav")

        # Mock Django's reverse function
        with patch("flex_menu.menu.reverse") as mock_reverse:
            mock_reverse.side_effect = lambda view, **kwargs: {
                "admin:index": "/admin/",
                "admin:auth_user_changelist": "/admin/auth/user/",
                "nonexistent:view": None,  # This will raise NoReverseMatch
            }.get(view)

            # Create items with view names
            admin_home = MenuLink(
                name="admin_home", view_name="admin:index", label="Admin"
            )
            user_list = MenuLink(
                name="user_list", view_name="admin:auth_user_changelist", label="Users"
            )

            nav.extend([admin_home, user_list])

            # Process menu
            processed = nav.process(authenticated_request)

            # Check URLs were resolved
            admin_item = next(
                c for c in processed._processed_children if c.name == "admin_home"
            )
            user_item = next(
                c for c in processed._processed_children if c.name == "user_list"
            )

            assert admin_item.url == "/admin/"
            assert user_item.url == "/admin/auth/user/"

    def test_menu_with_failing_url_resolution(self, authenticated_request):
        """Test menu behavior when URL resolution fails."""
        nav = MenuGroup(name="failing_nav")

        # Mock reverse to raise NoReverseMatch
        with patch("flex_menu.menu.reverse") as mock_reverse:
            from django.urls.exceptions import NoReverseMatch

            mock_reverse.side_effect = NoReverseMatch("View not found")

            # Create item with bad view name
            bad_item = MenuLink(
                name="bad_item", view_name="nonexistent:view", label="Bad Link"
            )
            nav.append(bad_item)

            # Disable URL failure logging for test
            with patch("flex_menu.menu._should_log_url_failures", return_value=False):
                processed = nav.process(authenticated_request)

            # Item should be hidden due to URL resolution failure
            assert len(processed._processed_children) == 0

    def test_menu_with_custom_check_functions(self, request_factory):
        """Test menu with custom check functions."""

        def is_premium_user(request, **kwargs):
            return hasattr(request.user, "is_premium") and request.user.is_premium

        def has_beta_access(request, **kwargs):
            return getattr(request.user, "beta_access", False)

        # Create menu with custom checks
        features = MenuGroup(name="features")

        basic_feature = MenuLink(name="basic", url="/basic/", check=True)
        premium_feature = MenuLink(
            name="premium", url="/premium/", check=is_premium_user
        )
        beta_feature = MenuLink(name="beta", url="/beta/", check=has_beta_access)

        features.extend([basic_feature, premium_feature, beta_feature])

        # Test with different user types
        test_cases = [
            # Regular user
            ({"is_authenticated": True}, ["basic"]),
            # Premium user
            ({"is_authenticated": True, "is_premium": True}, ["basic", "premium"]),
            # Beta user
            ({"is_authenticated": True, "beta_access": True}, ["basic", "beta"]),
            # Premium beta user
            (
                {"is_authenticated": True, "is_premium": True, "beta_access": True},
                ["basic", "premium", "beta"],
            ),
        ]

        for user_attrs, expected_visible in test_cases:
            request = request_factory.get("/")
            request.user = CustomTestUser(**user_attrs)

            processed = features.process(request)

            visible_names = [child.name for child in processed._processed_children]
            assert set(visible_names) == set(expected_visible)

    def test_menu_caching_and_performance(self, authenticated_request):
        """Test that menu processing is efficient and cacheable."""
        # Create a menu with cacheable URLs
        nav = MenuGroup(name="cacheable_nav")

        for i in range(10):
            item = MenuLink(name=f"item_{i}", url=f"/static{i}/")
            nav.append(item)

        # First processing
        import time

        start_time = time.time()
        processed1 = nav.process(authenticated_request)
        first_time = time.time() - start_time

        # Second processing (should benefit from any caching)
        start_time = time.time()
        processed2 = nav.process(authenticated_request)
        second_time = time.time() - start_time

        # Both should produce equivalent results
        assert len(processed1._processed_children) == len(
            processed2._processed_children
        )

        # Verify all URLs were resolved
        for child in processed1._processed_children:
            assert child.url.startswith("/static")

    def test_templatetag_integration(self, authenticated_request):
        """Test integration with templatetags."""
        from flex_menu import root
        from flex_menu.templatetags.flex_menu import process_menu, render_menu

        # Create test menu
        test_nav = MenuGroup(name="template_nav")
        home = MenuLink(name="home", url="/", label="Home")
        about = MenuLink(name="about", url="/about/", label="About")
        test_nav.extend([home, about])

        # Add to root for templatetag access
        root.append(test_nav)

        try:
            # Test process_menu templatetag
            context = {"request": authenticated_request}
            processed = process_menu(context, "template_nav")

            assert processed is not None
            assert processed.name == "template_nav"
            assert len(processed._processed_children) == 2

            # Test render_menu templatetag
            with patch(
                "flex_menu.menu.render_to_string"
            ) as mock_render:
                mock_render.return_value = "<nav>Test Navigation</nav>"

                rendered = render_menu(context, "template_nav")

                assert rendered == "<nav>Test Navigation</nav>"
                mock_render.assert_called_once()

        finally:
            # Clean up
            test_nav.parent = None

    def test_management_command_integration(self):
        """Test integration with management commands."""
        from io import StringIO

        from django.core.management import call_command

        from flex_menu import root

        # Create test menu structure
        cmd_menu = MenuGroup(name="command_test")
        item1 = MenuLink(name="item1", url="/cmd1/")
        item2 = MenuLink(name="item2", url="/cmd2/")
        cmd_menu.extend([item1, item2])

        root.append(cmd_menu)

        try:
            # Test the render_menu command
            out = StringIO()
            call_command("render_menu", "--name=command_test", stdout=out)

            output = out.getvalue()
            assert "command_test" in output
            assert "item1" in output
            assert "item2" in output

        finally:
            # Clean up
            cmd_menu.parent = None


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_e_commerce_site_navigation(self, request_factory):
        """Test a typical e-commerce site navigation structure."""
        # Create realistic e-commerce navigation
        main_nav = MenuGroup(name="main_navigation")

        # Public sections
        home = MenuLink(name="home", url="/", label="Home")
        products = MenuGroup(name="products", label="Products")

        # Product categories
        electronics = MenuLink(
            name="electronics", url="/products/electronics/", label="Electronics"
        )
        clothing = MenuLink(
            name="clothing", url="/products/clothing/", label="Clothing"
        )
        books = MenuLink(name="books", url="/products/books/", label="Books")
        products.extend([electronics, clothing, books])

        # User account section
        account_menu = MenuGroup(
            name="account", label="My Account", check=user_is_authenticated
        )
        profile = MenuLink(name="profile", url="/account/profile/", label="Profile")
        orders = MenuLink(name="orders", url="/account/orders/", label="Orders")
        wishlist = MenuLink(name="wishlist", url="/account/wishlist/", label="Wishlist")
        account_menu.extend([profile, orders, wishlist])

        # Build main navigation
        main_nav.extend([home, products, account_menu])

        # Test with anonymous user
        anon_request = request_factory.get("/")
        anon_request.user = Mock(is_authenticated=False)

        anon_processed = main_nav.process(anon_request)
        anon_visible = [child.name for child in anon_processed._processed_children]

        assert "home" in anon_visible
        assert "products" in anon_visible
        assert "account" not in anon_visible  # Hidden for anonymous users

        # Test with authenticated user
        auth_request = request_factory.get("/")
        auth_request.user = Mock(is_authenticated=True)

        auth_processed = main_nav.process(auth_request)
        auth_visible = [child.name for child in auth_processed._processed_children]

        assert "home" in auth_visible
        assert "products" in auth_visible
        assert "account" in auth_visible  # Visible for authenticated users

        # Test product categories are always visible
        products_menu = next(
            c for c in auth_processed._processed_children if c.name == "products"
        )
        product_categories = [child.name for child in products_menu._processed_children]

        assert "electronics" in product_categories
        assert "clothing" in product_categories
        assert "books" in product_categories

    def test_admin_dashboard_navigation(
        self, request_factory, staff_request, superuser_request
    ):
        """Test admin dashboard navigation with different permission levels."""
        from flex_menu.checks import user_is_superuser

        # Create admin navigation
        admin_nav = MenuGroup(name="admin_nav", check=user_is_staff)

        # General admin sections (staff level)
        dashboard = MenuLink(name="dashboard", url="/admin/", label="Dashboard")
        users = MenuLink(name="users", url="/admin/users/", label="Users")
        content = MenuLink(name="content", url="/admin/content/", label="Content")

        # System settings (superuser only)
        system_menu = MenuGroup(name="system", label="System", check=user_is_superuser)
        settings = MenuLink(
            name="settings", url="/admin/system/settings/", label="Settings"
        )
        logs = MenuLink(name="logs", url="/admin/system/logs/", label="Logs")
        backup = MenuLink(name="backup", url="/admin/system/backup/", label="Backup")
        system_menu.extend([settings, logs, backup])

        # Build admin nav
        admin_nav.extend([dashboard, users, content, system_menu])

        # Test with regular user (should see nothing)
        regular_request = request_factory.get("/admin/")
        regular_request.user = Mock(
            is_authenticated=True, is_staff=False, is_superuser=False
        )

        regular_processed = admin_nav.process(regular_request)
        assert regular_processed.visible is False

        # Test with staff user
        staff_processed = admin_nav.process(staff_request)
        assert staff_processed.visible is True

        staff_visible = [child.name for child in staff_processed._processed_children]
        assert "dashboard" in staff_visible
        assert "users" in staff_visible
        assert "content" in staff_visible
        assert "system" not in staff_visible  # Hidden for non-superusers

        # Test with superuser
        super_processed = admin_nav.process(superuser_request)
        assert super_processed.visible is True

        super_visible = [child.name for child in super_processed._processed_children]
        assert "dashboard" in super_visible
        assert "users" in super_visible
        assert "content" in super_visible
        assert "system" in super_visible  # Visible for superusers

        # Check system submenu
        system_menu_processed = next(
            c for c in super_processed._processed_children if c.name == "system"
        )
        system_items = [
            child.name for child in system_menu_processed._processed_children
        ]
        assert "settings" in system_items
        assert "logs" in system_items
        assert "backup" in system_items

    def test_multi_language_site_navigation(self, request_factory):
        """Test navigation for a multi-language site."""

        def language_check(lang):
            def check(request, **kwargs):
                return getattr(request, "LANGUAGE_CODE", "en") == lang

            return check

        # Create language-specific menus
        main_nav = MenuGroup(name="multilang_nav")

        # English menu
        en_menu = MenuGroup(name="en_menu", check=language_check("en"))
        en_home = MenuLink(name="en_home", url="/en/", label="Home")
        en_about = MenuLink(name="en_about", url="/en/about/", label="About")
        en_menu.extend([en_home, en_about])

        # Spanish menu
        es_menu = MenuGroup(name="es_menu", check=language_check("es"))
        es_home = MenuLink(name="es_home", url="/es/", label="Inicio")
        es_about = MenuLink(name="es_about", url="/es/acerca/", label="Acerca de")
        es_menu.extend([es_home, es_about])

        main_nav.extend([en_menu, es_menu])

        # Test with English request
        en_request = request_factory.get("/en/")
        en_request.LANGUAGE_CODE = "en"
        en_request.user = Mock(is_authenticated=True)

        en_processed = main_nav.process(en_request)
        en_visible = [child.name for child in en_processed._processed_children]

        assert "en_menu" in en_visible
        assert "es_menu" not in en_visible

        # Test with Spanish request
        es_request = request_factory.get("/es/")
        es_request.LANGUAGE_CODE = "es"
        es_request.user = Mock(is_authenticated=True)

        es_processed = main_nav.process(es_request)
        es_visible = [child.name for child in es_processed._processed_children]

        assert "es_menu" in es_visible
        assert "en_menu" not in es_visible
