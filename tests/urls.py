"""
URL configuration for django-flex-menus tests.
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Add test URLs here if needed for specific tests
]
