import os
import sys
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.ext import apidoc

sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("../plshandle"))

from plshandle import __version__

project = "plshandle"
copyright = "2020, Nicolas Kogler"
author = "Nicolas Kogler"

version = ".".join(__version__.split(".")[0:2])
release = __version__

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = None
exclude_patterns = [".build", "Thumbs.db", ".DS_Store"]
pygments_style = None

html_theme = "sphinx_rtd_theme"
htmlhelp_basename = "plshandle-doc"

epub_title = project
epub_exclude_files = ["search.html"]
