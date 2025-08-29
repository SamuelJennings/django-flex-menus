"""
Shared test configuration and fixtures for django-flex-menus.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import RequestFactory, override_settings

from flex_menu import root
from flex_menu.menu import BaseMenu, MenuGroup, MenuLink


@pytest.fixture
def request_factory():
    """Provides a Django RequestFactory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def mock_request(request_factory):
    """Creates a basic mock request."""
    request = request_factory.get("/test/")
    request.user = None  # Will be set by user fixtures
    return request


@pytest.fixture
def authenticated_request(request_factory, user):
    """Creates a mock request with an authenticated user."""
    request = request_factory.get("/test/")
    request.user = user
    return request


@pytest.fixture
def staff_request(request_factory, staff_user):
    """Creates a mock request with a staff user."""
    request = request_factory.get("/test/")
    request.user = staff_user
    return request


@pytest.fixture
def superuser_request(request_factory, superuser):
    """Creates a mock request with a superuser."""
    request = request_factory.get("/test/")
    request.user = superuser
    return request


@pytest.fixture
def user():
    """Creates a regular user."""
    import uuid

    User = get_user_model()
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f"testuser_{unique_id}",
        email=f"test_{unique_id}@example.com",
        password="testpass123",
    )


@pytest.fixture
def staff_user():
    """Creates a staff user."""
    import uuid

    User = get_user_model()
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f"staffuser_{unique_id}",
        email=f"staff_{unique_id}@example.com",
        password="testpass123",
        is_staff=True,
    )


@pytest.fixture
def superuser():
    """Creates a superuser."""
    import uuid

    User = get_user_model()
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_superuser(
        username=f"admin_{unique_id}",
        email=f"admin_{unique_id}@example.com",
        password="testpass123",
    )


@pytest.fixture
def user_with_permissions(user):
    """Creates a user with specific permissions."""
    permission = Permission.objects.get_or_create(
        codename="test_permission",
        name="Test Permission",
        content_type_id=1,  # Generic content type
    )[0]
    user.user_permissions.add(permission)
    return user


@pytest.fixture
def user_with_group(user):
    """Creates a user in a specific group."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    group = Group.objects.create(name=f"testgroup_{unique_id}")
    user.groups.add(group)
    # Store the group name for test reference
    user._test_group_name = group.name
    return user


@pytest.fixture
def base_menu():
    """Creates a basic BaseMenu instance."""
    return BaseMenu(name="test_base_menu")


@pytest.fixture
def menu():
    """Creates a basic MenuGroup instance."""
    return MenuGroup(name="test_menu")


@pytest.fixture
def menu_item():
    """Creates a basic MenuLink instance."""
    return MenuLink(name="test_item", url="/test/")


@pytest.fixture
def menu_item_with_view():
    """Creates a MenuLink with a view name."""
    return MenuLink(name="test_item_view", view_name="admin:index")


@pytest.fixture
def complex_menu_tree(menu):
    """Creates a complex menu tree for testing."""
    # Root menu
    home = MenuLink(name="home", url="/", label="Home")
    about = MenuLink(name="about", url="/about/", label="About")

    # Submenu with children
    products_menu = MenuGroup(name="products", label="Products")
    product1 = MenuLink(name="product1", url="/products/1/", label="Product 1")
    product2 = MenuLink(name="product2", url="/products/2/", label="Product 2")

    # Admin section
    admin_menu = MenuGroup(name="admin", label="Admin")
    admin_users = MenuLink(
        name="admin_users", view_name="admin:auth_user_changelist", label="Users"
    )
    admin_groups = MenuLink(
        name="admin_groups", view_name="admin:auth_group_changelist", label="Groups"
    )

    # Build tree
    menu.extend([home, about, products_menu, admin_menu])
    products_menu.extend([product1, product2])
    admin_menu.extend([admin_users, admin_groups])

    return menu


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Grants database access to all tests.
    """
    pass


@pytest.fixture
def settings_with_debug():
    """Provides settings with DEBUG=True for testing URL failure logging."""
    with override_settings(DEBUG=True, FLEX_MENU_LOG_URL_FAILURES=True):
        yield


@pytest.fixture
def settings_without_debug():
    """Provides settings with DEBUG=False for testing URL failure logging."""
    with override_settings(DEBUG=False, FLEX_MENU_LOG_URL_FAILURES=False):
        yield


@pytest.fixture(autouse=True)
def clean_root():
    # Backup children
    original_children = list(root.children)
    yield
    # Restore children
    root.children = original_children
    for child in root.children:
        child.parent = root
