def user_is_staff(request):
    return request.user.is_staff


def user_is_authenticated(request):
    return request.user.is_authenticated


def user_is_anonymous(request):
    return request.user.is_anonymous


def user_is_superuser(request):
    return request.user.is_superuser
