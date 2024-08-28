def is_staff_user(request):
    return request.user.is_staff
