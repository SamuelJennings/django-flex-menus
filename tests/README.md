"""
Test configuration file explaining how to run the django-flex-menus test suite.
"""

# Django Flex Menus Test Suite

This directory contains comprehensive tests for the django-flex-menus package.

## Test Structure

The test suite is organized into the following files:

### Core Functionality Tests
- `test_menu_core.py` - Comprehensive tests for BaseMenu, Menu, and MenuLink classes
- `test_menu.py` - Improved basic menu functionality tests (replaces original)
- `test_child_validation.py` - Tests for child class validation functionality (existing)

### Feature-Specific Tests
- `test_checks.py` - Tests for predefined check functions (user authentication, permissions, groups)
- `test_templatetags.py` - Tests for Django templatetags (process_menu, render_menu)
- `test_management_commands.py` - Tests for management commands (render_menu command)
- `test_apps.py` - Tests for Django app configuration and autodiscovery

### Integration & Performance Tests
- `test_integration.py` - End-to-end integration tests with real-world scenarios
- `test_performance.py` - Performance, thread safety, and memory usage tests

### Configuration
- `conftest.py` - Shared fixtures and pytest configuration

## Running the Tests

### Prerequisites
1. Install pytest and pytest-django:
   ```bash
   pip install pytest pytest-django
   ```

2. Ensure Django is properly configured in your environment

### Basic Test Runs

Run all tests:
```bash
pytest tests/
```

Run specific test files:
```bash
pytest tests/test_menu_core.py
pytest tests/test_checks.py
pytest tests/test_templatetags.py
```

Run tests by functionality:
```bash
# Core menu functionality
pytest tests/test_menu_core.py tests/test_menu.py

# Django integration
pytest tests/test_templatetags.py tests/test_management_commands.py tests/test_apps.py

# Validation and checks
pytest tests/test_child_validation.py tests/test_checks.py
```

### Advanced Test Options

Run integration tests:
```bash
pytest tests/test_integration.py -m integration
```

Run performance tests:
```bash
pytest tests/test_performance.py --run-performance
```

Run slow tests (threading, large structures):
```bash
pytest tests/ --run-slow
```

Skip performance and slow tests (default):
```bash
pytest tests/ -m "not performance and not slow"
```

### Test Coverage

Run with coverage reporting:
```bash
pip install pytest-cov
pytest tests/ --cov=flex_menu --cov-report=html
```

### Verbose Output

Run with detailed output:
```bash
pytest tests/ -v -s
```

## Test Categories

### Unit Tests
- `test_menu_core.py` - Core functionality
- `test_checks.py` - Check functions
- `test_child_validation.py` - Validation logic

### Integration Tests
- `test_templatetags.py` - Template integration
- `test_management_commands.py` - Command line integration
- `test_apps.py` - Django app integration
- `test_integration.py` - Full system integration

### Performance Tests
- `test_performance.py` - Marked with @pytest.mark.performance
- Thread safety tests
- Memory usage tests
- Large structure handling

## Test Data and Fixtures

The test suite includes comprehensive fixtures for:

### User Management
- Regular users (`user` fixture)
- Staff users (`staff_user` fixture)
- Superusers (`superuser` fixture)
- Users with permissions (`user_with_permissions` fixture)
- Users in groups (`user_with_group` fixture)

### Request Objects
- Basic mock requests (`mock_request` fixture)
- Authenticated requests (`authenticated_request` fixture)
- Staff requests (`staff_request` fixture)
- Superuser requests (`superuser_request` fixture)

### Menu Structures
- Basic menus (`menu`, `base_menu` fixtures)
- Menu items (`menu_item`, `menu_item_with_view` fixtures)
- Complex menu trees (`complex_menu_tree` fixture)

## Writing New Tests

When adding new tests, follow these guidelines:

1. **Use appropriate fixtures** - Leverage existing fixtures for common objects
2. **Group related tests** - Use test classes to organize related functionality
3. **Add docstrings** - Document what each test verifies
4. **Clean up** - Use fixtures that automatically clean up after tests
5. **Mark appropriately** - Use markers for performance/slow tests

Example test structure:
```python
class TestNewFeature:
    """Test the new feature functionality."""
    
    def test_basic_functionality(self, mock_request):
        \"\"\"Test basic feature behavior.\"\"\"
        # Test implementation
        pass
    
    def test_edge_case(self, mock_request):
        \"\"\"Test edge case handling.\"\"\"
        # Test implementation
        pass
```

## Common Test Patterns

### Testing Menu Visibility
```python
def test_menu_visibility(self, authenticated_request):
    menu = Menu(name="test", check=user_is_authenticated)
    processed = menu.process(authenticated_request)
    assert processed.visible is True
```

### Testing URL Resolution
```python
def test_url_resolution(self):
    item = MenuLink(name="test", url="/test/")
    assert item.resolve_url() == "/test/"
```

### Testing Check Functions
```python
def test_custom_check(self, mock_request):
    def custom_check(request, **kwargs):
        return request.user.is_staff
    
    mock_request.user.is_staff = True
    assert custom_check(mock_request) is True
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Django is properly configured and flex_menu is in INSTALLED_APPS
2. **Database Errors**: Tests use in-memory SQLite database configured in conftest.py
3. **Fixture Conflicts**: Use the `clear_menu_root` fixture to prevent test pollution

### Debug Mode

Enable debug output:
```bash
pytest tests/ -v -s --tb=long
```

### Specific Test Debugging

Run a single test with full output:
```bash
pytest tests/test_menu_core.py::TestBaseMenu::test_initialization -v -s
```

## Contributing Tests

When contributing new tests:

1. Ensure tests are well-documented
2. Use appropriate fixtures and markers
3. Test both success and failure cases
4. Include integration tests for new features
5. Add performance tests for potentially slow operations
6. Update this README if adding new test categories

## Test Environment

The test suite is configured to work with:
- Python 3.8+
- Django 3.2+
- pytest 6.0+
- pytest-django 4.0+

All tests should pass in both DEBUG=True and DEBUG=False modes.
