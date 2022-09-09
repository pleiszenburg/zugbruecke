:github_url:

.. _wineenv:

.. index::
	single: wenv
	single: wenv python
	single: wenv pip
	single: wenv pytest
	single: wenv init
	triple: wine; python; environment
	module: zugbruecke.wenv

Wine Python Environment
=======================

The ``wenv`` package
--------------------

*zugbruecke* runs on top of a *Windows* build of CPython on top of *Wine*. A dedicated *Wine Python Environment*, a special kind of Python virtual environment, is created underneath the currently activated *Unix Python Environment*. This entire mechanism is managed by a `dedicated Python package named wenv`_.

.. _dedicated Python package named wenv: https://wenv.readthedocs.io/

.. note::

	The functionality of ``wenv`` has its origin in *zugbruecke* and was eventually consolidated into its own separate Python package. ``wenv`` offers a sophisticated Command Line Interface (CLI) as well as an API for managing and working with *Windows Python* on top of *Wine*. For more details, see `wenv documentation`_.

.. _wenv documentation: https://wenv.readthedocs.io/

The ``zugbruecke.Env`` class
----------------------------

The *zugbruecke* package offers its own version of the ``wenv.Env`` class, essentially inheriting from it and extending it.

.. autoclass:: zugbruecke.Env
	:members:
	:show-inheritance:
	:inherited-members:
