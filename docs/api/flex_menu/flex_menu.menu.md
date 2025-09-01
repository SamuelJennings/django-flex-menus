# {py:mod}`flex_menu.menu`

```{py:module} flex_menu.menu
```

```{autodoc2-docstring} flex_menu.menu
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseMenu <flex_menu.menu.BaseMenu>`
  - ```{autodoc2-docstring} flex_menu.menu.BaseMenu
    :summary:
    ```
* - {py:obj}`MenuLink <flex_menu.menu.MenuLink>`
  -
* - {py:obj}`MenuItem <flex_menu.menu.MenuItem>`
  - ```{autodoc2-docstring} flex_menu.menu.MenuItem
    :summary:
    ```
* - {py:obj}`MenuGroup <flex_menu.menu.MenuGroup>`
  -
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_should_log_url_failures <flex_menu.menu._should_log_url_failures>`
  - ```{autodoc2-docstring} flex_menu.menu._should_log_url_failures
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`root <flex_menu.menu.root>`
  - ```{autodoc2-docstring} flex_menu.menu.root
    :summary:
    ```
* - {py:obj}`_NO_PARENT <flex_menu.menu._NO_PARENT>`
  - ```{autodoc2-docstring} flex_menu.menu._NO_PARENT
    :summary:
    ```
````

### API

````{py:function} _should_log_url_failures()
:canonical: flex_menu.menu._should_log_url_failures

```{autodoc2-docstring} flex_menu.menu._should_log_url_failures
```
````

`````{py:class} BaseMenu(name: str, parent: typing.Optional[flex_menu.menu.BaseMenu] = None, children: list[flex_menu.menu.BaseMenu] | None = None, check: collections.abc.Callable | bool = True, resolve_url: collections.abc.Callable | None = None, template_name: str | None = None, extra_context: dict | None = None, **kwargs)
:canonical: flex_menu.menu.BaseMenu

Bases: {py:obj}`anytree.Node`

```{autodoc2-docstring} flex_menu.menu.BaseMenu
```

```{rubric} Initialization
```

```{autodoc2-docstring} flex_menu.menu.BaseMenu.__init__
```

````{py:attribute} request
:canonical: flex_menu.menu.BaseMenu.request
:type: django.core.handlers.wsgi.WSGIRequest | None
:value: >
   None

```{autodoc2-docstring} flex_menu.menu.BaseMenu.request
```

````

````{py:attribute} template_name
:canonical: flex_menu.menu.BaseMenu.template_name
:value: >
   None

```{autodoc2-docstring} flex_menu.menu.BaseMenu.template_name
```

````

````{py:attribute} allowed_children
:canonical: flex_menu.menu.BaseMenu.allowed_children
:type: list[typing.Union[Type[BaseMenu], str]] | None
:value: >
   None

```{autodoc2-docstring} flex_menu.menu.BaseMenu.allowed_children
```

````

````{py:method} __str__() -> str
:canonical: flex_menu.menu.BaseMenu.__str__

````

````{py:method} __getitem__(name: str) -> flex_menu.menu.BaseMenu
:canonical: flex_menu.menu.BaseMenu.__getitem__

```{autodoc2-docstring} flex_menu.menu.BaseMenu.__getitem__
```

````

````{py:method} __iter__()
:canonical: flex_menu.menu.BaseMenu.__iter__

```{autodoc2-docstring} flex_menu.menu.BaseMenu.__iter__
```

````

````{py:method} _validate_child(child: flex_menu.menu.BaseMenu) -> None
:canonical: flex_menu.menu.BaseMenu._validate_child

```{autodoc2-docstring} flex_menu.menu.BaseMenu._validate_child
```

````

````{py:method} append(child: flex_menu.menu.BaseMenu) -> None
:canonical: flex_menu.menu.BaseMenu.append

```{autodoc2-docstring} flex_menu.menu.BaseMenu.append
```

````

````{py:method} extend(children: list[flex_menu.menu.BaseMenu]) -> None
:canonical: flex_menu.menu.BaseMenu.extend

```{autodoc2-docstring} flex_menu.menu.BaseMenu.extend
```

````

````{py:method} insert(children: typing.Union[flex_menu.menu.BaseMenu, list[flex_menu.menu.BaseMenu]], position: int) -> None
:canonical: flex_menu.menu.BaseMenu.insert

```{autodoc2-docstring} flex_menu.menu.BaseMenu.insert
```

````

````{py:method} insert_after(child: flex_menu.menu.BaseMenu, named: str) -> None
:canonical: flex_menu.menu.BaseMenu.insert_after

```{autodoc2-docstring} flex_menu.menu.BaseMenu.insert_after
```

````

````{py:method} pop(name: str | None = None) -> flex_menu.menu.BaseMenu
:canonical: flex_menu.menu.BaseMenu.pop

```{autodoc2-docstring} flex_menu.menu.BaseMenu.pop
```

````

````{py:method} get(name: str, maxlevel: int | None = None) -> typing.Optional[flex_menu.menu.BaseMenu]
:canonical: flex_menu.menu.BaseMenu.get

```{autodoc2-docstring} flex_menu.menu.BaseMenu.get
```

````

````{py:method} print_tree() -> str
:canonical: flex_menu.menu.BaseMenu.print_tree

```{autodoc2-docstring} flex_menu.menu.BaseMenu.print_tree
```

````

````{py:method} process(request, **kwargs) -> flex_menu.menu.BaseMenu
:canonical: flex_menu.menu.BaseMenu.process

```{autodoc2-docstring} flex_menu.menu.BaseMenu.process
```

````

````{py:method} _create_request_copy() -> flex_menu.menu.BaseMenu
:canonical: flex_menu.menu.BaseMenu._create_request_copy

```{autodoc2-docstring} flex_menu.menu.BaseMenu._create_request_copy
```

````

````{py:method} check(request, **kwargs) -> bool
:canonical: flex_menu.menu.BaseMenu.check

```{autodoc2-docstring} flex_menu.menu.BaseMenu.check
```

````

````{py:method} get_context_data(**kwargs) -> dict
:canonical: flex_menu.menu.BaseMenu.get_context_data

```{autodoc2-docstring} flex_menu.menu.BaseMenu.get_context_data
```

````

````{py:method} get_template_names() -> list[str]
:canonical: flex_menu.menu.BaseMenu.get_template_names

```{autodoc2-docstring} flex_menu.menu.BaseMenu.get_template_names
```

````

````{py:method} render(**kwargs)
:canonical: flex_menu.menu.BaseMenu.render

```{autodoc2-docstring} flex_menu.menu.BaseMenu.render
```

````

````{py:method} match_url() -> bool
:canonical: flex_menu.menu.BaseMenu.match_url

```{autodoc2-docstring} flex_menu.menu.BaseMenu.match_url
```

````

````{py:method} copy() -> flex_menu.menu.BaseMenu
:canonical: flex_menu.menu.BaseMenu.copy

```{autodoc2-docstring} flex_menu.menu.BaseMenu.copy
```

````

`````

````{py:data} root
:canonical: flex_menu.menu.root
:value: >
   'BaseMenu(...)'

```{autodoc2-docstring} flex_menu.menu.root
```

````

````{py:data} _NO_PARENT
:canonical: flex_menu.menu._NO_PARENT
:value: >
   'object(...)'

```{autodoc2-docstring} flex_menu.menu._NO_PARENT
```

````

`````{py:class} MenuLink(name: str, view_name: str = '', url: str = '', params: dict | None = None, template_name: str | None = None, extra_context: dict | None = None, **kwargs)
:canonical: flex_menu.menu.MenuLink

Bases: {py:obj}`flex_menu.menu.BaseMenu`

````{py:attribute} template_name
:canonical: flex_menu.menu.MenuLink.template_name
:value: >
   'menu/item.html'

```{autodoc2-docstring} flex_menu.menu.MenuLink.template_name
```

````

````{py:method} process(request, **kwargs)
:canonical: flex_menu.menu.MenuLink.process

````

````{py:method} resolve_url(*args, **kwargs)
:canonical: flex_menu.menu.MenuLink.resolve_url

```{autodoc2-docstring} flex_menu.menu.MenuLink.resolve_url
```

````

````{py:method} get_context_data(**kwargs) -> dict
:canonical: flex_menu.menu.MenuLink.get_context_data

```{autodoc2-docstring} flex_menu.menu.MenuLink.get_context_data
```

````

````{py:method} _create_request_copy() -> flex_menu.menu.MenuLink
:canonical: flex_menu.menu.MenuLink._create_request_copy

```{autodoc2-docstring} flex_menu.menu.MenuLink._create_request_copy
```

````

`````

`````{py:class} MenuItem(name: str, template_name: str | None = None, extra_context: dict | None = None, **kwargs)
:canonical: flex_menu.menu.MenuItem

Bases: {py:obj}`flex_menu.menu.BaseMenu`

```{autodoc2-docstring} flex_menu.menu.MenuItem
```

```{rubric} Initialization
```

```{autodoc2-docstring} flex_menu.menu.MenuItem.__init__
```

````{py:attribute} template_name
:canonical: flex_menu.menu.MenuItem.template_name
:value: >
   None

```{autodoc2-docstring} flex_menu.menu.MenuItem.template_name
```

````

````{py:method} _create_request_copy() -> flex_menu.menu.MenuItem
:canonical: flex_menu.menu.MenuItem._create_request_copy

```{autodoc2-docstring} flex_menu.menu.MenuItem._create_request_copy
```

````

`````

`````{py:class} MenuGroup(name, parent=None, children=None, template_name=None, extra_context=None, **kwargs)
:canonical: flex_menu.menu.MenuGroup

Bases: {py:obj}`flex_menu.menu.BaseMenu`

````{py:attribute} template_name
:canonical: flex_menu.menu.MenuGroup.template_name
:value: >
   'menu/menu.html'

```{autodoc2-docstring} flex_menu.menu.MenuGroup.template_name
```

````

````{py:method} process(request, **kwargs)
:canonical: flex_menu.menu.MenuGroup.process

````

````{py:property} processed_children
:canonical: flex_menu.menu.MenuGroup.processed_children

```{autodoc2-docstring} flex_menu.menu.MenuGroup.processed_children
```

````

````{py:method} get_context_data(**kwargs) -> dict
:canonical: flex_menu.menu.MenuGroup.get_context_data

```{autodoc2-docstring} flex_menu.menu.MenuGroup.get_context_data
```

````

````{py:method} _create_request_copy() -> flex_menu.menu.MenuGroup
:canonical: flex_menu.menu.MenuGroup._create_request_copy

```{autodoc2-docstring} flex_menu.menu.MenuGroup._create_request_copy
```

````

````{py:method} check(request, **kwargs) -> bool
:canonical: flex_menu.menu.MenuGroup.check

```{autodoc2-docstring} flex_menu.menu.MenuGroup.check
```

````

````{py:method} match_url() -> bool
:canonical: flex_menu.menu.MenuGroup.match_url

```{autodoc2-docstring} flex_menu.menu.MenuGroup.match_url
```

````

`````
