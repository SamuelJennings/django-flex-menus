import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

from docs.conf import *

autodoc2_packages = ["flex_menu"]

html_short_title = "Heatflow.world"
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
