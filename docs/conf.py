# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import sys
from pathlib import Path
# import matplotlib
# matplotlib.use('agg')

print(Path.cwd().parent)
# sys.path.insert(0, Path.cwd().parent)
sys.path.extend([str(Path.cwd().parent)])

print('Python %s on %s' % (sys.version, sys.platform))
print(sys.path)

# -- Project information -----------------------------------------------------

project = 'ONE'
copyright = '2021, International Brain Lab'
author = 'International Brain Lab'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = ''

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.autosummary',
              'sphinx.ext.mathjax',
              'sphinx.ext.githubpages',
              'sphinx_copybutton',
              'nbsphinx',
              'nbsphinx_link',
              'myst_parser',
              'sphinx.ext.napoleon',
              'sphinx.ext.viewcode']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']


#autoapi_add_toctree_entry = False
# autoapi_dirs = ['../*', '../one']
# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ['_build', '_templates', 'documentation_contribution_guidelines.md',
                    '.ipynb_checkpoints', 'templates', 'README.md', 'gh-pages']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = 'sphinx_rtd_theme'


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = ['css/style.css']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'onedoc'


# -- Options for LaTeX output ------------------------------------------------

# latex_elements = {
#     # The paper size ('letterpaper' or 'a4paper').
#     #
#     # 'papersize': 'letterpaper',
#
#     # The font size ('10pt', '11pt' or '12pt').
#     #
#     # 'pointsize': '10pt',
#
#     # Additional stuff for the LaTeX preamble.
#     #
#     # 'preamble': '',
#
#     # Latex figure (float) alignment
#     #
#     # 'figure_align': 'htbp',
# }
#
# # Grouping the document tree into LaTeX files. List of tuples
# # (source start file, target name, title,
# #  author, documentclass [howto, manual, or own class]).
# latex_documents = [
#     (master_doc, 'ONE.tex', 'ONE Documentation',
#      'International Brain Laboratory', 'manual'),
# ]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'ONE', 'ONE Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'ONE', 'ONE Documentation',
     author, 'ONE', 'Open Neurophysiology Envrionment.',
     'Miscellaneous'),
]


# -- Options for autosummary and autodoc ------------------------------------
autosummary_generate = True
# Don't add module names to function docs
add_module_names = False

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'show-inheritance': False
}


def param_line_break(app, what, name, obj, options, lines):
    first_param = next((i for i, j in enumerate(lines) if ':param' in j), -1)
    if first_param != -1:
        # if the first param is not preceded by a line break add one in
        if lines[first_param - 1] != '':
            lines.insert(first_param, '')
    return


def setup(app):
    # Connect the autodoc-skip-member event from apidoc to the callback
    app.connect('autodoc-process-docstring', param_line_break)


# -- Options for nbsphinx ------------------------------------

# Only use nbsphinx for formatting the notebooks i.e never execute
nbsphinx_execute = 'never'
# Cancel compile on errors in notebooks
nbsphinx_allow_errors = False
# Add cell execution out number
nbsphinx_output_prompt = 'Out[%s]:'
# Configuration for images
nbsphinx_execute_arguments = [
    "--InlineBackend.figure_formats={'svg', 'pdf'}",
    "--InlineBackend.rc={'figure.dpi': 96}",
]
plot_formats = [('png', 512)]

# Add extra prolog to beginning of each .ipynb file
# Add option to download notebook and link to github page
nbsphinx_prolog = r"""

{% if env.metadata[env.docname]['nbsphinx-link-target'] %}
{% set nb_path = env.metadata[env.docname]['nbsphinx-link-target'] | dirname %}
{% set nb_name = env.metadata[env.docname]['nbsphinx-link-target'] | basename %}
{% else %}
{% set nb_name = env.doc2path(env.docname, base=None) | basename %}
{% set nb_path = env.doc2path(env.docname, base=None) | dirname %}
{% endif %}

.. raw:: html

      <a href="{{ nb_name }}"><button id="download">Download tutorial notebook</button></a>
      <a href="https://github.com/int-brain-lab/ONE/tree/main/docs_gh_pages/{{ nb_path }}/
      {{ nb_name }}"><button id="github">Github link</button></a>

# """
