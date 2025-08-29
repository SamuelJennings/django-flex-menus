"""
Tests for the predefined check functions in django-flex-menus.
"""

from unittest.mock import Mock, patch

import pytest
from django.test import RequestFactory

from flex_menu.checks import (
    combine_checks,
    debug_mode_only,
    negate_check,
    request_is_ajax,
    request_is_secure,
    request_method_is,
    user_attribute_equals,
    user_email_verified,
    user_has_all_permissions,
    user_has_any_permission,
    user_has_object_permission,
    user_has_profile,
    user_in_all_groups,
    user_in_any_group,
    user_in_group_with_permission,
    user_is_active,
    user_is_anonymous,
    user_is_authenticated,
    user_is_staff,
    user_is_superuser,
)


class TestUserChecks:
    """Test user-based check functions."""

    def test_user_is_staff_with_staff_user(self, staff_request):
        """Test user_is_staff with staff user."""
        assert user_is_staff(staff_request) is True

    def test_user_is_staff_with_regular_user(self, authenticated_request):
        """Test user_is_staff with regular user."""
        assert user_is_staff(authenticated_request) is False

    def test_user_is_authenticated_with_authenticated_user(self, authenticated_request):
        """Test user_is_authenticated with authenticated user."""
        assert user_is_authenticated(authenticated_request) is True

    def test_user_is_authenticated_with_anonymous_user(self, mock_request):
        """Test user_is_authenticated with anonymous user."""
        mock_user = Mock()
        mock_user.is_authenticated = False
        mock_request.user = mock_user

        assert user_is_authenticated(mock_request) is False

    def test_user_is_anonymous_with_anonymous_user(self, mock_request):
        """Test user_is_anonymous with anonymous user."""
        mock_user = Mock()
        mock_user.is_anonymous = True
        mock_request.user = mock_user

        assert user_is_anonymous(mock_request) is True

    def test_user_is_anonymous_with_authenticated_user(self, authenticated_request):
        """Test user_is_anonymous with authenticated user."""
        assert user_is_anonymous(authenticated_request) is False

    def test_user_is_superuser_with_superuser(self, superuser_request):
        """Test user_is_superuser with superuser."""
        assert user_is_superuser(superuser_request) is True

    def test_user_is_superuser_with_regular_user(self, authenticated_request):
        """Test user_is_superuser with regular user."""
        assert user_is_superuser(authenticated_request) is False


class TestGroupChecks:
    """Test group-based check functions."""

    def test_user_in_any_group_single_group_match(
        self, user_with_group, request_factory
    ):
        """Test user_in_any_group with user in specified group."""
        request = request_factory.get("/")
        request.user = user_with_group

        group_name = user_with_group._test_group_name
        check_func = user_in_any_group(group_name)
        assert check_func(request) is True

    def test_user_in_any_group_no_match(self, user_with_group, request_factory):
        """Test user_in_any_group with user not in any specified group."""
        request = request_factory.get("/")
        request.user = user_with_group

        check_func = user_in_any_group("othergroup", "differentgroup")
        assert check_func(request) is False

    def test_user_in_any_group_anonymous_user(self, mock_request):
        """Test user_in_any_group with anonymous user."""
        mock_user = Mock()
        mock_user.is_authenticated = False
        mock_request.user = mock_user

        check_func = user_in_any_group("testgroup")
        assert check_func(mock_request) is False


class TestPermissionChecks:
    """Test permission-based check functions."""

    def test_user_has_any_permission_with_permission(
        self, user_with_permissions, request_factory
    ):
        """Test user_has_any_permission with user having required permission."""
        request = request_factory.get("/")
        request.user = user_with_permissions

        # Mock has_perm to return True for our test permission
        user_with_permissions.has_perm = Mock(return_value=True)

        check_func = user_has_any_permission("test.test_permission")
        assert check_func(request) is True
        user_with_permissions.has_perm.assert_called_with("test.test_permission")

    def test_user_has_any_permission_multiple_perms_has_one(
        self, user_with_permissions, request_factory
    ):
        """Test user_has_any_permission with multiple permissions, user has one."""
        request = request_factory.get("/")
        request.user = user_with_permissions

        # Mock has_perm to return True for second permission only
        def mock_has_perm(perm):
            return perm == "test.second_permission"

        user_with_permissions.has_perm = Mock(side_effect=mock_has_perm)

        check_func = user_has_any_permission(
            "test.first_permission", "test.second_permission"
        )
        assert check_func(request) is True

    def test_user_has_any_permission_without_permission(self, authenticated_request):
        """Test user_has_any_permission with user lacking required permission."""
        authenticated_request.user.has_perm = Mock(return_value=False)

        check_func = user_has_any_permission("test.test_permission")
        assert check_func(authenticated_request) is False

    def test_user_has_any_permission_anonymous_user(self, mock_request):
        """Test user_has_any_permission with anonymous user."""
        mock_user = Mock()
        mock_user.is_authenticated = False
        mock_request.user = mock_user

        check_func = user_has_any_permission("test.test_permission")
        assert check_func(mock_request) is False


class TestDeprecatedChecks:
    """Test deprecated check functions."""

    def test_user_has_object_permission_deprecated(self, authenticated_request):
        """Test that user_has_object_permission shows deprecation warning."""
        check_func = user_has_object_permission("test.change_object")

        with pytest.warns(
            DeprecationWarning, match="user_has_object_permission is deprecated"
        ):
            result = check_func(authenticated_request)

        assert result is False


class TestCheckFunctionIntegration:
    """Test integration of check functions with menu items."""

    def test_staff_only_menu_item(self, staff_request, authenticated_request):
        """Test menu item that's only visible to staff."""
        from flex_menu.menu import MenuLink

        staff_item = MenuLink(name="staff_only", url="/admin/", check=user_is_staff)

        # Staff user should see it
        staff_processed = staff_item.process(staff_request)
        assert staff_processed.visible is True

        # Regular user should not
        regular_processed = staff_item.process(authenticated_request)
        assert regular_processed.visible is False

    def test_group_based_menu_item(self, user_with_group, request_factory):
        """Test menu item visible only to specific group members."""
        from django.contrib.auth import get_user_model

        from flex_menu.menu import MenuLink

        # Create a separate user that is NOT in any group
        User = get_user_model()
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        regular_user = User.objects.create_user(
            username=f"regular_{unique_id}",
            email=f"regular_{unique_id}@example.com",
            password="testpass123",
        )

        # Use the dynamic group name from the fixture
        group_name = user_with_group._test_group_name
        group_item = MenuLink(
            name="group_only", url="/group-area/", check=user_in_any_group(group_name)
        )

        # User in group should see it
        group_request = request_factory.get("/")
        group_request.user = user_with_group
        group_processed = group_item.process(group_request)
        assert group_processed.visible is True

        # User not in group should not
        regular_request = request_factory.get("/")
        regular_request.user = regular_user
        regular_processed = group_item.process(regular_request)
        assert regular_processed.visible is False

    def test_permission_based_menu_item(
        self, user_with_permissions, authenticated_request, request_factory
    ):
        """Test menu item visible only to users with specific permissions."""
        from flex_menu.menu import MenuLink

        # Mock the permission check
        user_with_permissions.has_perm = Mock(return_value=True)

        perm_item = MenuLink(
            name="perm_only",
            url="/admin-area/",
            check=user_has_any_permission("test.test_permission"),
        )

        # User with permission should see it
        perm_request = request_factory.get("/")
        perm_request.user = user_with_permissions
        perm_processed = perm_item.process(perm_request)
        assert perm_processed.visible is True

        # User without permission should not
        authenticated_request.user.has_perm = Mock(return_value=False)
        regular_processed = perm_item.process(authenticated_request)
        assert regular_processed.visible is False

    def test_multiple_check_functions_combined(
        self, superuser_request, staff_request, authenticated_request
    ):
        """Test combining multiple check functions."""
        from flex_menu.menu import MenuLink

        def admin_check(request, **kwargs):
            return user_is_staff(request) or user_is_superuser(request)

        admin_item = MenuLink(name="admin_area", url="/admin/", check=admin_check)

        # Superuser should see it
        super_processed = admin_item.process(superuser_request)
        assert super_processed.visible is True

        # Staff should see it
        staff_processed = admin_item.process(staff_request)
        assert staff_processed.visible is True

        # Regular user should not
        regular_processed = admin_item.process(authenticated_request)
        assert regular_processed.visible is False


class TestNewUserChecks:
    """Test new user-based check functions."""

    def test_user_is_active_with_active_user(self, authenticated_request):
        """Test user_is_active with active user."""
        authenticated_request.user.is_active = True
        assert user_is_active(authenticated_request) is True

    def test_user_is_active_with_inactive_user(self, authenticated_request):
        """Test user_is_active with inactive user."""
        authenticated_request.user.is_active = False
        assert user_is_active(authenticated_request) is False

    def test_user_is_active_with_no_user(self):
        """Test user_is_active with request that has no user."""
        request = Mock()
        delattr(request, 'user') if hasattr(request, 'user') else None
        assert user_is_active(request) is False

    def test_user_email_verified_with_verified_user(self, authenticated_request):
        """Test user_email_verified with verified user."""
        authenticated_request.user.email_verified = True
        assert user_email_verified(authenticated_request) is True

    def test_user_email_verified_with_unverified_user(self, authenticated_request):
        """Test user_email_verified with unverified user."""
        authenticated_request.user.email_verified = False
        assert user_email_verified(authenticated_request) is False

    def test_user_email_verified_no_field(self, authenticated_request):
        """Test user_email_verified when user model has no email_verified field."""
        # Ensure the field doesn't exist
        if hasattr(authenticated_request.user, 'email_verified'):
            delattr(authenticated_request.user, 'email_verified')
        
        # Should return True for authenticated users without the field
        assert user_email_verified(authenticated_request) is True

    def test_user_has_profile_with_profile(self, authenticated_request):
        """Test user_has_profile with user that has a profile."""
        authenticated_request.user.profile = Mock()
        assert user_has_profile(authenticated_request) is True

    def test_user_has_profile_no_profile_attr(self, authenticated_request):
        """Test user_has_profile when user has no profile attribute."""
        # Remove any profile attributes
        for attr in ['profile', 'userprofile', 'user_profile']:
            if hasattr(authenticated_request.user, attr):
                delattr(authenticated_request.user, attr)
        
        # Should return True when no profile model is detected
        assert user_has_profile(authenticated_request) is True


class TestNewGroupChecks:
    """Test new group-based check functions."""

    def test_user_in_all_groups_match_all(self, user_with_group, request_factory):
        """Test user_in_all_groups when user is in all specified groups."""
        from django.contrib.auth.models import Group
        
        request = request_factory.get("/")
        request.user = user_with_group
        
        # Create another group and add user to it
        group2 = Group.objects.create(name="testgroup2")
        user_with_group.groups.add(group2)
        
        group1_name = user_with_group._test_group_name
        check_func = user_in_all_groups(group1_name, "testgroup2")
        assert check_func(request) is True

    def test_user_in_all_groups_missing_one(self, user_with_group, request_factory):
        """Test user_in_all_groups when user is missing one group."""
        request = request_factory.get("/")
        request.user = user_with_group
        
        group1_name = user_with_group._test_group_name
        check_func = user_in_all_groups(group1_name, "nonexistent_group")
        assert check_func(request) is False

    def test_user_in_group_with_permission_success(self, user_with_group, request_factory):
        """Test user_in_group_with_permission when user has both group and permission."""
        request = request_factory.get("/")
        request.user = user_with_group
        
        # Mock the has_perm method
        user_with_group.has_perm = Mock(return_value=True)
        
        group_name = user_with_group._test_group_name
        check_func = user_in_group_with_permission(group_name, "test.test_permission")
        assert check_func(request) is True

    def test_user_in_group_with_permission_no_permission(self, user_with_group, request_factory):
        """Test user_in_group_with_permission when user has group but no permission."""
        request = request_factory.get("/")
        request.user = user_with_group
        
        # Mock the has_perm method to return False
        user_with_group.has_perm = Mock(return_value=False)
        
        group_name = user_with_group._test_group_name
        check_func = user_in_group_with_permission(group_name, "test.test_permission")
        assert check_func(request) is False


class TestNewPermissionChecks:
    """Test new permission-based check functions."""

    def test_user_has_all_permissions_success(self, user_with_permissions, request_factory):
        """Test user_has_all_permissions when user has all permissions."""
        request = request_factory.get("/")
        request.user = user_with_permissions
        
        # Mock has_perm to return True for all permissions
        user_with_permissions.has_perm = Mock(return_value=True)
        
        check_func = user_has_all_permissions("test.perm1", "test.perm2")
        assert check_func(request) is True

    def test_user_has_all_permissions_missing_one(self, user_with_permissions, request_factory):
        """Test user_has_all_permissions when user is missing one permission."""
        request = request_factory.get("/")
        request.user = user_with_permissions
        
        # Mock has_perm to return False for one permission
        def mock_has_perm(perm):
            return perm != "test.perm2"
        
        user_with_permissions.has_perm = Mock(side_effect=mock_has_perm)
        
        check_func = user_has_all_permissions("test.perm1", "test.perm2")
        assert check_func(request) is False


class TestRequestChecks:
    """Test request-based check functions."""

    def test_request_is_ajax_true(self):
        """Test request_is_ajax with AJAX request."""
        factory = RequestFactory()
        request = factory.get("/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert request_is_ajax(request) is True

    def test_request_is_ajax_false(self):
        """Test request_is_ajax with non-AJAX request."""
        factory = RequestFactory()
        request = factory.get("/")
        assert request_is_ajax(request) is False

    def test_request_is_secure_true(self):
        """Test request_is_secure with secure request."""
        factory = RequestFactory()
        request = factory.get("/", secure=True)
        assert request_is_secure(request) is True

    def test_request_is_secure_false(self):
        """Test request_is_secure with non-secure request."""
        factory = RequestFactory()
        request = factory.get("/")
        assert request_is_secure(request) is False

    def test_request_method_is_match(self):
        """Test request_method_is with matching method."""
        factory = RequestFactory()
        request = factory.post("/")
        
        check_func = request_method_is("POST", "PUT")
        assert check_func(request) is True

    def test_request_method_is_no_match(self):
        """Test request_method_is with non-matching method."""
        factory = RequestFactory()
        request = factory.get("/")
        
        check_func = request_method_is("POST", "PUT")
        assert check_func(request) is False


class TestUtilityChecks:
    """Test utility check functions."""

    def test_user_attribute_equals_match(self, authenticated_request):
        """Test user_attribute_equals with matching attribute."""
        authenticated_request.user.subscription_type = "premium"
        
        check_func = user_attribute_equals("subscription_type", "premium")
        assert check_func(authenticated_request) is True

    def test_user_attribute_equals_no_match(self, authenticated_request):
        """Test user_attribute_equals with non-matching attribute."""
        authenticated_request.user.subscription_type = "basic"
        
        check_func = user_attribute_equals("subscription_type", "premium")
        assert check_func(authenticated_request) is False

    def test_user_attribute_equals_no_attribute(self, authenticated_request):
        """Test user_attribute_equals when attribute doesn't exist."""
        check_func = user_attribute_equals("nonexistent_attr", "value")
        assert check_func(authenticated_request) is False

    @patch('django.conf.settings.DEBUG', True)
    def test_debug_mode_only_true(self, mock_request):
        """Test debug_mode_only when DEBUG=True."""
        assert debug_mode_only(mock_request) is True

    @patch('django.conf.settings.DEBUG', False)
    def test_debug_mode_only_false(self, mock_request):
        """Test debug_mode_only when DEBUG=False."""
        assert debug_mode_only(mock_request) is False


class TestCombinationChecks:
    """Test check combination functions."""

    def test_combine_checks_and_all_true(self, authenticated_request):
        """Test combine_checks with AND logic when all checks are True."""
        def check1(request, **kwargs):
            return True
        
        def check2(request, **kwargs):
            return True
        
        combined = combine_checks(check1, check2, operator='and')
        assert combined(authenticated_request) is True

    def test_combine_checks_and_one_false(self, authenticated_request):
        """Test combine_checks with AND logic when one check is False."""
        def check1(request, **kwargs):
            return True
        
        def check2(request, **kwargs):
            return False
        
        combined = combine_checks(check1, check2, operator='and')
        assert combined(authenticated_request) is False

    def test_combine_checks_or_one_true(self, authenticated_request):
        """Test combine_checks with OR logic when one check is True."""
        def check1(request, **kwargs):
            return True
        
        def check2(request, **kwargs):
            return False
        
        combined = combine_checks(check1, check2, operator='or')
        assert combined(authenticated_request) is True

    def test_combine_checks_or_all_false(self, authenticated_request):
        """Test combine_checks with OR logic when all checks are False."""
        def check1(request, **kwargs):
            return False
        
        def check2(request, **kwargs):
            return False
        
        combined = combine_checks(check1, check2, operator='or')
        assert combined(authenticated_request) is False

    def test_negate_check_true_becomes_false(self, authenticated_request):
        """Test negate_check with a function that returns True."""
        def always_true(request, **kwargs):
            return True
        
        negated = negate_check(always_true)
        assert negated(authenticated_request) is False

    def test_negate_check_false_becomes_true(self, authenticated_request):
        """Test negate_check with a function that returns False."""
        def always_false(request, **kwargs):
            return False
        
        negated = negate_check(always_false)
        assert negated(authenticated_request) is True


@pytest.mark.django_db
def test_user_in_all_groups_edge_cases(request_factory, django_user_model):
    from flex_menu.checks import user_in_all_groups
    request = request_factory.get("/")
    # No user
    request.user = None
    check = user_in_all_groups("group1", "group2")
    assert check(request) is False
    # Anonymous user
    class Anon:
        is_authenticated = False
    request.user = Anon()
    assert check(request) is False
    # Authenticated user missing one group
    user = django_user_model.objects.create_user(username="u1", password="x")
    request.user = user
    user.groups.clear()
    assert check(request) is False
    # Authenticated user in all groups
    from django.contrib.auth.models import Group
    g1 = Group.objects.create(name="group1")
    g2 = Group.objects.create(name="group2")
    user.groups.add(g1, g2)
    assert check(request) is True


def test_user_has_all_permissions_edge_cases(request_factory, django_user_model):
    from flex_menu.checks import user_has_all_permissions
    request = request_factory.get("/")
    # No user
    request.user = None
    check = user_has_all_permissions("perm1", "perm2")
    assert check(request) is False
    # Anonymous user
    class Anon:
        is_authenticated = False
    request.user = Anon()
    assert check(request) is False
    # Authenticated user missing one perm
    user = django_user_model.objects.create_user(username="u2", password="x")
    request.user = user
    user.has_perm = Mock(side_effect=lambda p: p == "perm1")
    assert check(request) is False
    # Authenticated user with all perms
    user.has_perm = Mock(return_value=True)
    assert check(request) is True


def test_user_is_active_edge_cases(request_factory, django_user_model):
    from flex_menu.checks import user_is_active
    request = request_factory.get("/")
    # No user
    request.user = None
    assert user_is_active(request) is False
    # Inactive user
    class User:
        is_active = False
    request.user = User()
    assert user_is_active(request) is False
    # Active user
    class User2:
        is_active = True
    request.user = User2()
    assert user_is_active(request) is True
    # Django user (should be active by default)
    user = django_user_model.objects.create_user(username="u3", password="x")
    request.user = user
    assert user_is_active(request) is True


def test_user_email_verified_edge_cases(request_factory, django_user_model):
    from flex_menu.checks import user_email_verified
    request = request_factory.get("/")
    # No user
    request.user = None
    assert user_email_verified(request) is False
    # Not authenticated
    class Anon:
        is_authenticated = False
    request.user = Anon()
    assert user_email_verified(request) is False
    # Authenticated, no email_verified attr
    class User:
        is_authenticated = True
    request.user = User()
    assert user_email_verified(request) is True
    # Authenticated, email_verified False
    class User2:
        is_authenticated = True
        email_verified = False
    request.user = User2()
    assert user_email_verified(request) is False
    # Authenticated, email_verified True
    class User3:
        is_authenticated = True
        email_verified = True
    request.user = User3()
    assert user_email_verified(request) is True


def test_user_has_profile_edge_cases(request_factory, django_user_model):
    from flex_menu.checks import user_has_profile
    request = request_factory.get("/")
    # No user
    request.user = None
    assert user_has_profile(request) is False
    # Not authenticated
    class Anon:
        is_authenticated = False
    request.user = Anon()
    assert user_has_profile(request) is False
    # Authenticated, no profile attr
    class User:
        is_authenticated = True
    request.user = User()
    assert user_has_profile(request) is True
    # Authenticated, with profile attr
    class User2:
        is_authenticated = True
        profile = object()
    request.user = User2()
    assert user_has_profile(request) is True
    # Authenticated, with profile attr None
    class User3:
        is_authenticated = True
        profile = None
    request.user = User3()
    assert user_has_profile(request) is False
    # Authenticated, AttributeError
    class User4:
        is_authenticated = True
        def __getattr__(self, name):
            raise AttributeError()
    request.user = User4()
    assert user_has_profile(request) is True


def test_user_attribute_equals_edge_cases(request_factory, django_user_model):
    from flex_menu.checks import user_attribute_equals
    request = request_factory.get("/")
    # Not authenticated
    class Anon:
        is_authenticated = False
    request.user = Anon
    check = user_attribute_equals("foo", "bar")
    assert check(request) is False
    # Authenticated, attribute present and matches
    class User:
        is_authenticated = True
        foo = "bar"
    request.user = User()
    assert check(request) is True
    # Authenticated, attribute present and does not match
    class User2:
        is_authenticated = True
        foo = "baz"
    request.user = User2()
    assert check(request) is False
    # Authenticated, attribute not present
    class User3:
        is_authenticated = True
    request.user = User3()
    assert check(request) is False


def test_user_in_group_with_permission_edge_cases(request_factory, django_user_model):
    from flex_menu.checks import user_in_group_with_permission
    request = request_factory.get("/")
    # Not authenticated
    class Anon:
        is_authenticated = False
        groups = Mock()
        def has_perm(self, perm): return False
    request.user = Anon()
    check = user_in_group_with_permission("group", "perm")
    assert check(request) is False
    # Authenticated, not in group
    class User:
        is_authenticated = True
        groups = Mock()
        def has_perm(self, perm): return True
    user = User()
    user.groups.filter.return_value.exists.return_value = False
    request.user = user
    assert check(request) is False
    # Authenticated, in group, no permission
    user.groups.filter.return_value.exists.return_value = True
    user.has_perm = Mock(return_value=False)
    assert check(request) is False
    # Authenticated, in group, has permission
    user.has_perm = Mock(return_value=True)
    assert check(request) is True
