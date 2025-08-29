from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from flex_menu.menu import MenuGroup, MenuItem, MenuLink


class BS5NavbarItem(MenuLink):
    """
    Bootstrap 5 navbar link item.
    Renders as <li class="nav-item"><a class="nav-link">
    """

    template_name = "bootstrap5/navbar/item.html"


class BS5NavbarDropdownItem(MenuLink):
    """
    Bootstrap 5 navbar dropdown item.
    Renders as <li><a class="dropdown-item">
    """

    template_name = "bootstrap5/navbar/dropdown_item.html"


class BS5NavbarDropdownDivider(MenuItem):
    """
    Bootstrap 5 navbar dropdown divider.
    Renders as <li><hr class="dropdown-divider">
    """

    template_name = "bootstrap5/navbar/dropdown_divider.html"

    def __init__(self, name="divider", **kwargs):
        super().__init__(name, **kwargs)


class BS5NavbarDropdown(MenuGroup):
    """
    Bootstrap 5 navbar dropdown menu.
    Renders as <li class="nav-item dropdown">
    """

    template_name = "bootstrap5/navbar/dropdown_menu.html"
    allowed_children = [BS5NavbarDropdownItem, BS5NavbarDropdownDivider]


class BS5NavbarMultilevelDropdown(MenuGroup):
    """
    Bootstrap 5 navbar multi-level dropdown menu (supports nesting).
    Renders as <li class="nav-item dropdown">
    Allows nested dropdowns for complex menu structures.
    """

    template_name = "bootstrap5/navbar/multilevel_dropdown_menu.html"
    allowed_children = [BS5NavbarDropdownItem, BS5NavbarDropdownDivider, "self"]


class BS5NavbarMenu(MenuGroup):
    """
    Bootstrap 5 navbar menu container.
    Renders as <ul class="navbar-nav">
    """

    # "bootstrap5/navbar/navbar.html"
    template_name = "bootstrap5/navbar/menu.html"
    allowed_children = [BS5NavbarItem, BS5NavbarDropdown]


class BS5ListGroupItem(MenuLink):
    """
    Bootstrap 5 list-group item.
    Renders as <a class="list-group-item list-group-item-action">
    """

    template_name = "bootstrap5/list-group/item.html"


class BS5ListGroupSubItem(MenuLink):
    """
    Bootstrap 5 list-group sub-item for nested menus.
    Renders as <a class="list-group-item list-group-item-action ps-4">
    """

    template_name = "bootstrap5/list-group/sub_item.html"


class BS5ListGroupDivider(MenuItem):
    """
    Bootstrap 5 list-group divider.
    Renders as <div class="list-group-item bg-light border-0 py-1">
    """

    template_name = "bootstrap5/list-group/divider.html"

    def __init__(self, name="divider", **kwargs):
        super().__init__(name, **kwargs)


class BS5ListGroupSubmenu(MenuGroup):
    """
    Bootstrap 5 list-group submenu container.
    Renders as a collapsible section within the list group.
    """

    template_name = "bootstrap5/list-group/submenu.html"
    allowed_children = [BS5ListGroupSubItem, BS5ListGroupDivider]


class BS5ListGroupMenu(MenuGroup):
    """
    Bootstrap 5 list-group menu container.
    Renders as <div class="list-group">
    """

    template_name = "bootstrap5/list-group/menu.html"
    allowed_children = [BS5ListGroupItem, BS5ListGroupSubmenu]


site_nav = BS5NavbarMenu(
    "site_nav",
    children=[
        BS5NavbarItem("Home", view_name="home", extra_context={"label": "Home"}),
        BS5NavbarItem(
            "About",
            view_name="about",
            extra_context={"label": "About"},
        ),
        BS5NavbarDropdown(
            "Services",
            extra_context={"label": "Services"},
            children=[
                BS5NavbarDropdownItem(
                    "Web Design",
                    view_name="web_design",
                    extra_context={
                        "label": "Web Design",
                        "icon": "fas fa-palette",
                    },
                ),
                BS5NavbarDropdownItem(
                    "Development",
                    view_name="development",
                    extra_context={"label": "Development", "icon": "fas fa-code"},
                ),
                BS5NavbarDropdownDivider(),
                BS5NavbarDropdownItem(
                    "Consulting",
                    view_name="consulting",
                    extra_context={
                        "label": "Consulting",
                        "icon": "fas fa-handshake",
                    },
                ),
            ],
        ),
        BS5NavbarItem(
            "Contact",
            view_name="contact",
            extra_context={"label": "Contact"},
        ),
    ],
)


# Bootstrap 5 List Group Menu - Duplicate of site_nav
sidebar_nav = BS5ListGroupMenu(
    "sidebar_nav",
    children=[
        BS5ListGroupItem("Home", view_name="home", extra_context={"label": "Home", "icon": "fas fa-home"}),
        BS5ListGroupItem(
            "About",
            view_name="about",
            extra_context={"label": "About", "icon": "fas fa-info-circle"},
        ),
        BS5ListGroupSubmenu(
            "Services",
            extra_context={"label": "Services", "icon": "fas fa-cogs"},
            children=[
                BS5ListGroupSubItem(
                    "Web Design",
                    view_name="web_design",
                    extra_context={
                        "label": "Web Design",
                        "icon": "fas fa-palette",
                    },
                ),
                BS5ListGroupSubItem(
                    "Development",
                    view_name="development",
                    extra_context={"label": "Development", "icon": "fas fa-code"},
                ),
                BS5ListGroupSubItem(
                    "Consulting",
                    view_name="consulting",
                    extra_context={
                        "label": "Consulting",
                        "icon": "fas fa-handshake",
                    },
                ),
            ],
        ),
        BS5ListGroupItem(
            "Contact",
            view_name="contact",
            extra_context={"label": "Contact", "icon": "fas fa-envelope"},
        ),
    ],
)
