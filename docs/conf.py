import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


sys.path.insert(0, str(BASE_DIR / "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

from docs.conf import *

autodoc2_packages = [
    {
        "path": "../src/flex_menu",   # path to your package
        "module": "flex_menu",        # import name of the package
    }
]
autodoc2_render_plugin = "myst"  # or "rst"
autodoc2_output_dir = "api"
html_logo = None
html_favicon = None
html_short_title = "Django Flex Menus"
# html_theme_options.update(
#     {
#         "icon_links": [
#             {
#                 "name": "Heat Flow World",
#                 "url": "https://heatflow.world",
#                 "icon": "_static/icon.svg",
#                 "type": "local",
#             },
#         ],
#     }
# )

html_theme_options["path_to_docs"] = "docs"
html_theme_options["home_page_in_toc"] = False
extensions += [
    "sphinx_design",
    "sphinx_exec_code",
]

myst_allow_raw_html = True
myst_title_to_header = False

myst_html_meta = {
    "description lang=en": "Documentation and guides for the Heatflow.world web portal.",
    "keywords": "heat flow, Global Heat Flow Database, geothermal, heat flow, geophysics, geology",
}


autodoc2_parse_docstrings = True

autodoc2_docstring_parser_regexes = [("myst", r".*choices*")]
