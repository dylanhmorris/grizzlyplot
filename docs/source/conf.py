# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GrizzlyPlot'
copyright = '2023, Dylan H. Morris'
author = 'Dylan H. Morris'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'numpydoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.inheritance_diagram',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']
html_theme_options = {}

autosummary_generate = True
autosummary_imported_members = True
autosummary_ignore_module_all = False
autodoc_typehints_format = "short"
autodoc_typehints = "signature"
autodoc_type_aliases = {
    "ArrayLike": ":class:`numpy.typing.ArrayLike`",
    ":class:`numpy.typing.ArrayLike`": "ArrayLike"
}


intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'numpyro': ('https://num.pyro.ai/en/latest/', None),
    'jax': ('https://jax.readthedocs.io/en/latest/', None),
    'polars': ('https://pola-rs.github.io/polars/py-polars/html', None),
}
