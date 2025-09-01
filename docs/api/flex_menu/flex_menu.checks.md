# {py:mod}`flex_menu.checks`

```{py:module} flex_menu.checks
```

```{autodoc2-docstring} flex_menu.checks
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`user_is_staff <flex_menu.checks.user_is_staff>`
  - ```{autodoc2-docstring} flex_menu.checks.user_is_staff
    :summary:
    ```
* - {py:obj}`user_is_authenticated <flex_menu.checks.user_is_authenticated>`
  - ```{autodoc2-docstring} flex_menu.checks.user_is_authenticated
    :summary:
    ```
* - {py:obj}`user_is_anonymous <flex_menu.checks.user_is_anonymous>`
  - ```{autodoc2-docstring} flex_menu.checks.user_is_anonymous
    :summary:
    ```
* - {py:obj}`user_is_superuser <flex_menu.checks.user_is_superuser>`
  - ```{autodoc2-docstring} flex_menu.checks.user_is_superuser
    :summary:
    ```
* - {py:obj}`user_in_any_group <flex_menu.checks.user_in_any_group>`
  - ```{autodoc2-docstring} flex_menu.checks.user_in_any_group
    :summary:
    ```
* - {py:obj}`user_has_any_permission <flex_menu.checks.user_has_any_permission>`
  - ```{autodoc2-docstring} flex_menu.checks.user_has_any_permission
    :summary:
    ```
* - {py:obj}`user_has_object_permission <flex_menu.checks.user_has_object_permission>`
  - ```{autodoc2-docstring} flex_menu.checks.user_has_object_permission
    :summary:
    ```
* - {py:obj}`user_in_all_groups <flex_menu.checks.user_in_all_groups>`
  - ```{autodoc2-docstring} flex_menu.checks.user_in_all_groups
    :summary:
    ```
* - {py:obj}`user_has_all_permissions <flex_menu.checks.user_has_all_permissions>`
  - ```{autodoc2-docstring} flex_menu.checks.user_has_all_permissions
    :summary:
    ```
* - {py:obj}`user_is_active <flex_menu.checks.user_is_active>`
  - ```{autodoc2-docstring} flex_menu.checks.user_is_active
    :summary:
    ```
* - {py:obj}`user_email_verified <flex_menu.checks.user_email_verified>`
  - ```{autodoc2-docstring} flex_menu.checks.user_email_verified
    :summary:
    ```
* - {py:obj}`user_has_profile <flex_menu.checks.user_has_profile>`
  - ```{autodoc2-docstring} flex_menu.checks.user_has_profile
    :summary:
    ```
* - {py:obj}`request_is_ajax <flex_menu.checks.request_is_ajax>`
  - ```{autodoc2-docstring} flex_menu.checks.request_is_ajax
    :summary:
    ```
* - {py:obj}`request_is_secure <flex_menu.checks.request_is_secure>`
  - ```{autodoc2-docstring} flex_menu.checks.request_is_secure
    :summary:
    ```
* - {py:obj}`request_method_is <flex_menu.checks.request_method_is>`
  - ```{autodoc2-docstring} flex_menu.checks.request_method_is
    :summary:
    ```
* - {py:obj}`user_attribute_equals <flex_menu.checks.user_attribute_equals>`
  - ```{autodoc2-docstring} flex_menu.checks.user_attribute_equals
    :summary:
    ```
* - {py:obj}`user_in_group_with_permission <flex_menu.checks.user_in_group_with_permission>`
  - ```{autodoc2-docstring} flex_menu.checks.user_in_group_with_permission
    :summary:
    ```
* - {py:obj}`debug_mode_only <flex_menu.checks.debug_mode_only>`
  - ```{autodoc2-docstring} flex_menu.checks.debug_mode_only
    :summary:
    ```
* - {py:obj}`combine_checks <flex_menu.checks.combine_checks>`
  - ```{autodoc2-docstring} flex_menu.checks.combine_checks
    :summary:
    ```
* - {py:obj}`negate_check <flex_menu.checks.negate_check>`
  - ```{autodoc2-docstring} flex_menu.checks.negate_check
    :summary:
    ```
````

### API

````{py:function} user_is_staff(request, **kwargs)
:canonical: flex_menu.checks.user_is_staff

```{autodoc2-docstring} flex_menu.checks.user_is_staff
```
````

````{py:function} user_is_authenticated(request, **kwargs)
:canonical: flex_menu.checks.user_is_authenticated

```{autodoc2-docstring} flex_menu.checks.user_is_authenticated
```
````

````{py:function} user_is_anonymous(request, **kwargs)
:canonical: flex_menu.checks.user_is_anonymous

```{autodoc2-docstring} flex_menu.checks.user_is_anonymous
```
````

````{py:function} user_is_superuser(request, **kwargs)
:canonical: flex_menu.checks.user_is_superuser

```{autodoc2-docstring} flex_menu.checks.user_is_superuser
```
````

````{py:function} user_in_any_group(*groups)
:canonical: flex_menu.checks.user_in_any_group

```{autodoc2-docstring} flex_menu.checks.user_in_any_group
```
````

````{py:function} user_has_any_permission(*perms: str)
:canonical: flex_menu.checks.user_has_any_permission

```{autodoc2-docstring} flex_menu.checks.user_has_any_permission
```
````

````{py:function} user_has_object_permission(perm: str)
:canonical: flex_menu.checks.user_has_object_permission

```{autodoc2-docstring} flex_menu.checks.user_has_object_permission
```
````

````{py:function} user_in_all_groups(*groups)
:canonical: flex_menu.checks.user_in_all_groups

```{autodoc2-docstring} flex_menu.checks.user_in_all_groups
```
````

````{py:function} user_has_all_permissions(*perms: str)
:canonical: flex_menu.checks.user_has_all_permissions

```{autodoc2-docstring} flex_menu.checks.user_has_all_permissions
```
````

````{py:function} user_is_active(request, **kwargs)
:canonical: flex_menu.checks.user_is_active

```{autodoc2-docstring} flex_menu.checks.user_is_active
```
````

````{py:function} user_email_verified(request, **kwargs)
:canonical: flex_menu.checks.user_email_verified

```{autodoc2-docstring} flex_menu.checks.user_email_verified
```
````

````{py:function} user_has_profile(request, **kwargs)
:canonical: flex_menu.checks.user_has_profile

```{autodoc2-docstring} flex_menu.checks.user_has_profile
```
````

````{py:function} request_is_ajax(request, **kwargs)
:canonical: flex_menu.checks.request_is_ajax

```{autodoc2-docstring} flex_menu.checks.request_is_ajax
```
````

````{py:function} request_is_secure(request, **kwargs)
:canonical: flex_menu.checks.request_is_secure

```{autodoc2-docstring} flex_menu.checks.request_is_secure
```
````

````{py:function} request_method_is(*methods)
:canonical: flex_menu.checks.request_method_is

```{autodoc2-docstring} flex_menu.checks.request_method_is
```
````

````{py:function} user_attribute_equals(attribute_name: str, expected_value)
:canonical: flex_menu.checks.user_attribute_equals

```{autodoc2-docstring} flex_menu.checks.user_attribute_equals
```
````

````{py:function} user_in_group_with_permission(group_name: str, permission: str)
:canonical: flex_menu.checks.user_in_group_with_permission

```{autodoc2-docstring} flex_menu.checks.user_in_group_with_permission
```
````

````{py:function} debug_mode_only(request, **kwargs)
:canonical: flex_menu.checks.debug_mode_only

```{autodoc2-docstring} flex_menu.checks.debug_mode_only
```
````

````{py:function} combine_checks(*check_functions, operator='and')
:canonical: flex_menu.checks.combine_checks

```{autodoc2-docstring} flex_menu.checks.combine_checks
```
````

````{py:function} negate_check(check_function)
:canonical: flex_menu.checks.negate_check

```{autodoc2-docstring} flex_menu.checks.negate_check
```
````
