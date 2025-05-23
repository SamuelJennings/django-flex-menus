def user_is_staff(request, **kwargs):
    """
    Check if the user associated with the given request is a staff member.

    Returns:
        bool: True if the user is a staff member, False otherwise.
    """
    return request.user.is_staff


def user_is_authenticated(request, **kwargs):
    """
    Checks if the user associated with the given request is authenticated.

    Returns:
        bool: True if the user is authenticated, False otherwise.
    """
    return request.user.is_authenticated


def user_is_anonymous(request, **kwargs):
    """
    Check if the user associated with the given request is anonymous.

    Returns:
        bool: True if the user is anonymous, False otherwise.
    """
    return request.user.is_anonymous


def user_is_superuser(request, **kwargs):
    """
    Check if the user associated with the given request is a superuser.

    Returns:
        bool: True if the user is a superuser, False otherwise.
    """
    return request.user.is_superuser


def user_in_any_group(*groups):
    """
    Checks if the authenticated user belongs to any of the specified groups.

    Args:
        *groups: Variable length argument list of group names to check against.
    Returns:
        function: A function that takes a Django request object and optional keyword arguments,
                  and returns True if the user is authenticated and is a member of any of the specified groups,
                  otherwise False.
    Example:
        MenuItem(
            name="Authors only",
            view_name="author-management-page",
            check=user_in_any_group('authors'),
            )
    """

    def _function(request, **kwargs):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name__in=groups).exists()
        )

    return _function


def user_has_any_permission(*perms: str):
    """
    Checks if the current user has at least one of the specified permissions.

    Args:
        *perms (str): One or more permission strings to check against the user.
    Returns:
        bool: True if the user has at least one of the specified permissions, False otherwise.
    Example:
        MenuItem(
            name="Authors",
            view_name="book-create",
            check=user_has_any_permission('book.add_book'),
            )
    """

    def _check(request, **kwargs):
        return request.user.is_authenticated and any(
            request.user.has_perm(perm) for perm in perms
        )

    return _check


def user_has_object_permission(perm: str):
    """
    Checks if the requesting user has a specific object-level permission.

    Args:
        perm (str): The permission codename to check (e.g., 'blog.change_post').
    Returns:
        bool: True if the user has the specified permission on the object, False otherwise.
    Note:
        This check requires django-guardian to be installed and configured for object-level permissions.
    """

    def _check(request, instance, **kwargs):
        return request.user.has_perm("blog.change_post", instance)

    return _check
