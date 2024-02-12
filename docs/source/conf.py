# Configuration file for the Sphinx documentation builder.

# -- Project information
import sys
import os

sys.path.append(os.path.abspath("../.."))
sys.path.append(os.path.abspath("extensions"))

project = 'Quant'
copyright = '2024, MagM1go and contributors'
author = 'MagM1go'

release = '0.1'
version = '1.5'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'attributetable'
]

autodoc_default_options = {"members": True, "show-inheritance": True}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'furo'
pygments_style = "monokai"
default_dark_mode = True

# -- Options for EPUB output
epub_show_urls = 'footnote'

rst_prolog = """
.. |corofunc| replace: This is a |coroutine_link|_ function 
"""