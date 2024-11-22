import pytest

from flex_menu.menu import BaseMenu, Menu, MenuItem


@pytest.fixture
def menu():
    return Menu(name="test_menu")


@pytest.fixture
def child_item():
    return MenuItem(name="child_item", view_name="test_view")


@pytest.fixture
def child_menu():
    return Menu(name="child_menu")


class MockRequest:
    def __init__(self, path):
        self.path = path


def test_menu_initialization(menu):
    assert menu.name == "test_menu"
    assert menu.label == "test_menu"
    assert menu.check is None
    assert menu.resolve_url is None


def test_menu_append(menu, child_item):
    menu.append(child_item)
    assert child_item in menu.children
    assert child_item.menu == menu


def test_menu_extend(menu, child_item):
    child2 = BaseMenu(name="child2")
    menu.extend([child_item, child2])
    assert child_item in menu.children
    assert child2 in menu.children
    assert child_item.menu == menu
    assert child2.menu == menu


def test_menu_insert(menu, child_item):
    child2 = BaseMenu(name="child2")
    menu.append(child_item)
    menu.insert(child2, position=0)
    assert menu.children[0] == child2
    assert menu.children[1] == child_item


def test_menu_insert_after(menu, child_item):
    child2 = BaseMenu(name="child2")
    menu.append(child_item)
    menu.insert_after(child2, named="child_item")
    assert menu.children[1] == child2


def test_menu_pop(menu, child_item):
    menu.append(child_item)
    removed_child = menu.pop("child")
    assert removed_child == child_item
    assert child_item not in menu.children


def test_menu_get(menu, child_item):
    menu.append(child_item)
    found_child = menu.get("child")
    assert found_child == child_item


def test_menu_render(menu, child_item):
    menu.append(child_item)
    rendered = menu.render(menu, child_item)
    assert "menu" in rendered
    assert "child_item" in rendered


def test_menu_process(menu, child_item):
    def check_func(request, **kwargs):
        return request.path == "/test"

    request = MockRequest(path="/test")
    menu.process(request)
    assert menu.visible


def test_menu_match_url(menu, child_item):
    menu.url = "/test"
    request = MockRequest(path="/test")
    assert menu.match_url(request)


def test_menu_copy(menu, child_item):
    menu_copy = menu.copy()
    assert menu_copy.name == menu.name
    assert menu_copy is not menu


def test_menu_item_initialization(menu, child_item):
    with pytest.raises(ValueError):
        MenuItem(name="test_item")

    item = MenuItem(name="test_item", view_name="test_view")
    assert item.view_name == "test_view"
    assert item.url == ""


def test_menu_item_process(menu, child_item):
    item = MenuItem(name="test_item", view_name="test_view")
    request = MockRequest(path="/test")
    item.process(request)
    assert item.visible


def test_menu_item_resolve_url(menu, child_item):
    item = MenuItem(name="test_item", view_name="test_view")
    request = MockRequest(path="/test")
    resolved_url = item.resolve_url(request)
    assert resolved_url is None


# def test_menu_initialization(menu, child_item):
#     menu = Menu(name="test_menu")
#     assert menu.menu == menu.root


# def test_menu_process(menu, child_item):
#     menu = Menu(name="test_menu")
#     child = MenuItem(name="child_item", view_name="test_view")
#     menu.append(child)
#     request = MockRequest(path="/test")
#     menu.process(request)
#     assert child.visible


# def test_menu_check(menu, child_item):
#     menu = Menu(name="test_menu")
#     child = MenuItem(name="child_item", view_name="test_view")
#     menu.append(child)
#     request = MockRequest(path="/test")
#     assert menu.check(request)


# def test_menu_match_url(menu, child_item):
#     menu = Menu(name="test_menu")
#     child = MenuItem(name="child_item", view_name="test_view")
#     menu.append(child)
#     request = MockRequest(path="/test")
#     assert not menu.match_url(request)
