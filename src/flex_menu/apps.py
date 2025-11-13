from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class FlexMenuConfig(AppConfig):
    name = "flex_menu"

    def ready(self):
        autodiscover_modules("menus")

        # Warm the URL params cache to ensure fast lookups from the start
        from .utils import warm_url_params_cache

        warm_url_params_cache()
