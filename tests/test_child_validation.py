"""
Test child class validation functionality
"""

import pytest

from flex_menu.menu import MenuGroup, MenuItem, MenuLink


class TestChildValidation:
    """Test the allowed_children functionality"""

    def test_no_validation_by_default(self):
        """When allowed_children is None, any child should be allowed"""
        menu = MenuGroup("Test")
        item = MenuLink("Item", url="/")

        # Should not raise any error
        menu.append(item)
        assert len(menu.children) == 1

    def test_class_based_validation_success(self):
        """Valid child classes should be accepted"""

        class SpecificMenuLink(MenuLink):
            pass

        class SpecificMenu(MenuGroup):
            allowed_children = [SpecificMenuLink]

        menu = SpecificMenu("Test")
        item = SpecificMenuLink("Item", url="/")

        # Should not raise any error
        menu.append(item)
        assert len(menu.children) == 1

    def test_class_based_validation_failure(self):
        """Invalid child classes should be rejected"""

        class SpecificMenuLink(MenuLink):
            pass

        class WrongMenuLink(MenuLink):
            pass

        class SpecificMenu(MenuGroup):
            allowed_children = [SpecificMenuLink]

        menu = SpecificMenu("Test")
        wrong_item = WrongMenuLink("Wrong", url="/")

        # Should raise TypeError
        with pytest.raises(TypeError) as exc_info:
            menu.append(wrong_item)

        error_msg = str(exc_info.value)
        assert "SpecificMenu only allows children of types" in error_msg
        assert "SpecificMenuLink" in error_msg
        assert "WrongMenuLink" in error_msg

    def test_inheritance_works(self):
        """Child classes should accept subclasses of allowed types"""

        class BaseMenuLink(MenuLink):
            pass

        class SpecificMenuLink(BaseMenuLink):
            pass

        class MenuWithBase(MenuGroup):
            allowed_children = [BaseMenuLink]

        menu = MenuWithBase("Test")
        specific_item = SpecificMenuLink("Specific", url="/")

        # Should not raise error - SpecificMenuLink inherits from BaseMenuLink
        menu.append(specific_item)
        assert len(menu.children) == 1

    def test_multiple_allowed_types(self):
        """Should accept any of multiple allowed types"""

        class TypeA(MenuLink):
            pass

        class TypeB(MenuLink):
            pass

        class TypeC(MenuLink):
            pass

        class FlexibleMenu(MenuGroup):
            allowed_children = [TypeA, TypeB]

        menu = FlexibleMenu("Test")

        # Both TypeA and TypeB should work
        menu.append(TypeA("A", url="/"))
        menu.append(TypeB("B", url="/"))
        assert len(menu.children) == 2

        # TypeC should fail
        with pytest.raises(TypeError):
            menu.append(TypeC("C", url="/"))

    def test_validation_in_extend(self):
        """extend() should validate all items before adding any"""

        class ValidItem(MenuLink):
            pass

        class InvalidItem(MenuLink):
            pass

        class ValidatingMenu(MenuGroup):
            allowed_children = [ValidItem]

        menu = ValidatingMenu("Test")

        # Mix of valid and invalid items
        items = [
            ValidItem("Valid1", url="/"),
            InvalidItem("Invalid", url="/"),  # This makes the whole extend fail
            ValidItem("Valid2", url="/"),
        ]

        # Should raise error and add NO items
        with pytest.raises(TypeError):
            menu.extend(items)

        assert len(menu.children) == 0  # Nothing should be added

    def test_real_world_bootstrap_example(self):
        """Test a realistic Bootstrap 5 dropdown scenario"""

        class Bootstrap5DropdownMenuLink(MenuLink):
            template = "bootstrap5/dropdown-item.html"

        class Bootstrap5DropdownDivider(MenuItem):
            template_name = "bootstrap5/dropdown-divider.html"

        class Bootstrap5DropdownMenu(MenuGroup):
            template_name = "bootstrap5/dropdown-menu.html"
            allowed_children = [Bootstrap5DropdownMenuLink, Bootstrap5DropdownDivider]

        # Build a typical dropdown
        dropdown = Bootstrap5DropdownMenu("User MenuGroup")
        dropdown.append(Bootstrap5DropdownMenuLink("Profile", url="/profile"))
        dropdown.append(Bootstrap5DropdownDivider("divider"))
        dropdown.append(Bootstrap5DropdownMenuLink("Logout", url="/logout"))

        assert len(dropdown.children) == 3

        # Regular MenuLink should fail
        regular_item = MenuLink("Settings", url="/settings")
        with pytest.raises(TypeError) as exc_info:
            dropdown.append(regular_item)

        error_msg = str(exc_info.value)
        assert "Bootstrap5DropdownMenu only allows children of types" in error_msg
        assert "Bootstrap5DropdownMenuLink" in error_msg
        assert "Bootstrap5DropdownDivider" in error_msg

    def test_allowed_children_with_custom_types(self):
        """Test allowed_children validation with custom menu types."""

        class SpecialItem(MenuLink):
            pass

        class RestrictedMenu(MenuGroup):
            allowed_children = [SpecialItem]

        menu = RestrictedMenu(name="restricted")

        # Should allow SpecialItem
        special_item = SpecialItem(name="special", url="/special/")
        menu.append(special_item)  # Should not raise

        # Should reject regular MenuLink
        regular_item = MenuLink(name="regular", url="/regular/")
        with pytest.raises(TypeError):
            menu.append(regular_item)

    def test_self_reference_in_allowed_children(self):
        """Test that 'self' in allowed_children allows instances of the same class"""

        class NestedDropdown(MenuGroup):
            template_name = "nested_dropdown.html"
            allowed_children = ["self", MenuLink]

        # Create a parent dropdown
        parent_dropdown = NestedDropdown("parent")
        
        # Should be able to add regular menu links
        link = MenuLink("link", url="/link/")
        parent_dropdown.append(link)
        
        # Should be able to add another NestedDropdown (self-reference)
        child_dropdown = NestedDropdown("child")
        parent_dropdown.append(child_dropdown)
        
        # Should be able to nest multiple levels
        grandchild_dropdown = NestedDropdown("grandchild")
        child_dropdown.append(grandchild_dropdown)
        
        assert len(parent_dropdown.children) == 2
        assert len(child_dropdown.children) == 1
        assert isinstance(parent_dropdown.children[1], NestedDropdown)
        assert isinstance(child_dropdown.children[0], NestedDropdown)

    def test_self_reference_rejects_other_classes(self):
        """Test that 'self' reference still rejects other unallowed classes"""

        class StrictDropdown(MenuGroup):
            allowed_children = ["self"]  # Only allow instances of StrictDropdown

        dropdown = StrictDropdown("parent")
        
        # Should allow another StrictDropdown
        child_dropdown = StrictDropdown("child")
        dropdown.append(child_dropdown)  # Should not raise
        
        # Should reject MenuLink (not in allowed_children)
        link = MenuLink("link", url="/link/")
        with pytest.raises(TypeError) as exc_info:
            dropdown.append(link)
        
        error_msg = str(exc_info.value)
        assert "StrictDropdown only allows children of types" in error_msg
        assert "StrictDropdown" in error_msg  # Should show the actual class name, not "self"
        assert "MenuLink" in error_msg

    def test_self_reference_with_inheritance(self):
        """Test that 'self' reference works with inheritance"""

        class BaseDropdown(MenuGroup):
            allowed_children = ["self"]

        class SpecialDropdown(BaseDropdown):
            pass

        # Base dropdown should accept other base dropdowns
        base1 = BaseDropdown("base1")
        base2 = BaseDropdown("base2")
        base1.append(base2)  # Should work
        
        # Special dropdown should accept other special dropdowns
        special1 = SpecialDropdown("special1")
        special2 = SpecialDropdown("special2")
        special1.append(special2)  # Should work
        
        # Base should not accept special (different classes)
        with pytest.raises(TypeError):
            base1.append(special1)
        
        # Special should not accept base (different classes)
        with pytest.raises(TypeError):
            special1.append(base1)

    def test_multi_level_nested_menu_example(self):
        """Test a realistic multi-level nested menu scenario"""

        class MultilevelDropdown(MenuGroup):
            template_name = "multilevel_dropdown.html"
            allowed_children = ["self", MenuLink, MenuItem]

        # Build a complex nested structure
        main_menu = MultilevelDropdown("main")
        
        # Add some regular links
        main_menu.append(MenuLink("home", url="/"))
        main_menu.append(MenuLink("about", url="/about/"))
        
        # Add a nested submenu
        services_menu = MultilevelDropdown("services")
        services_menu.append(MenuLink("web_design", url="/services/web-design/"))
        services_menu.append(MenuLink("development", url="/services/development/"))
        
        # Add a nested sub-submenu
        development_submenu = MultilevelDropdown("development_types")
        development_submenu.append(MenuLink("frontend", url="/services/development/frontend/"))
        development_submenu.append(MenuLink("backend", url="/services/development/backend/"))
        
        services_menu.append(development_submenu)
        main_menu.append(services_menu)
        
        # Add a divider and contact link
        main_menu.append(MenuItem("divider"))
        main_menu.append(MenuLink("contact", url="/contact/"))
        
        # Verify structure
        assert len(main_menu.children) == 5  # home, about, services, divider, contact
        assert len(services_menu.children) == 3  # web_design, development, development_types
        assert len(development_submenu.children) == 2  # frontend, backend
        
        # Verify types
        assert isinstance(main_menu.children[2], MultilevelDropdown)  # services menu
        assert isinstance(services_menu.children[2], MultilevelDropdown)  # development submenu

    def test_self_reference_mixed_with_classes(self):
        """Test 'self' reference mixed with other allowed classes"""

        class SpecialLink(MenuLink):
            pass

        class FlexibleDropdown(MenuGroup):
            allowed_children = [SpecialLink, "self", MenuItem]

        dropdown = FlexibleDropdown("flexible")
        
        # Should accept SpecialLink
        dropdown.append(SpecialLink("special", url="/special/"))
        
        # Should accept self (another FlexibleDropdown)
        dropdown.append(FlexibleDropdown("child"))
        
        # Should accept MenuItem
        dropdown.append(MenuItem("divider"))
        
        # Should reject regular MenuLink (not in allowed list)
        with pytest.raises(TypeError):
            dropdown.append(MenuLink("regular", url="/regular/"))
        
        assert len(dropdown.children) == 3
