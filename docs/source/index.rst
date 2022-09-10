:github_url:

.. image:: _static/logo.png
    :alt: zugbruecke

zugbruecke
==========

**Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD**

*/ˈt͡suːkˌbʁʏkə/* - German, noun, feminine: `drawbridge`_

.. _drawbridge: https://dict.leo.org/englisch-deutsch/zugbrücke

.. |build_master| image:: https://github.com/pleiszenburg/zugbruecke/actions/workflows/test.yaml/badge.svg?branch=master
	:target: https://github.com/pleiszenburg/zugbruecke/actions/workflows/test.yaml
	:alt: Test Status: master / release
.. |docs_master| image:: https://readthedocs.org/projects/zugbruecke/badge/?version=latest&style=flat-square
	:target: http://zugbruecke.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status: master / release
.. |license| image:: https://img.shields.io/pypi/l/zugbruecke.svg?style=flat-square
	:target: https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE
	:alt: Project License: LGPLv2
.. |status| image:: https://img.shields.io/pypi/status/zugbruecke.svg?style=flat-square
	:target: https://github.com/pleiszenburg/zugbruecke/milestone/1
	:alt: Project Development Status
.. |pypi_version| image:: https://img.shields.io/pypi/v/zugbruecke.svg?style=flat-square
	:target: https://pypi.python.org/pypi/zugbruecke
	:alt: Available on PyPi - the Python Package Index
.. |pypi_versions| image:: https://img.shields.io/pypi/pyversions/zugbruecke.svg?style=flat-square
	:target: https://pypi.python.org/pypi/zugbruecke
	:alt: Available on PyPi - the Python Package Index
.. |chat| image:: https://img.shields.io/matrix/zugbruecke:matrix.org.svg?style=flat-square
	:target: https://matrix.to/#/#zugbruecke:matrix.org
	:alt: Matrix Chat Room
.. |mailing_list| image:: https://img.shields.io/badge/mailing%20list-groups.io-8cbcd1.svg?style=flat-square
	:target: https://groups.io/g/zugbruecke-dev
	:alt: Mailing List

|build_master| |docs_master| |license| |status| |pypi_version| |pypi_versions| |chat| |mailing_list|

User's guide
------------

*zugbruecke* is a drop-in replacement for *ctypes* with minimal, *ctypes*-compatible syntax extensions.

.. warning::

    This manual describes what makes *zugbruecke* special and how it differs from *ctypes*. It does **NOT** substitute the `ctypes documentation`_. Please read the latter first if you have never called foreign functions with *ctypes* from *Python* scripts.

.. _ctypes documentation: https://docs.python.org/3/library/ctypes.html?highlight=ctypes#module-ctypes

.. toctree::
    :maxdepth: 2
    :caption: Introduction

    introduction
    installation
    examples

.. toctree::
    :maxdepth: 2
    :caption: Reference

    session
    configuration
    memsync
    interoperability
    wineenv

.. toctree::
    :maxdepth: 2
    :caption: Advanced

    benchmarks
    security
    bugs
    changes
    faq
    support

`Interested in contributing?`_

.. _Interested in contributing?: https://github.com/pleiszenburg/zugbruecke/blob/develop/CONTRIBUTING.rst

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`
