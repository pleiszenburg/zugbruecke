:github_url:

.. image:: http://www.pleiszenburg.de/zugbruecke_logo.png
    :alt: zugbruecke

Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD.

User's guide
------------

*zugbruecke* is a drop-in replacement for *ctypes* with minimal, *ctypes*-compatible syntax extensions.
This manual describes what makes *zugbruecke* special and how it differs from *ctypes*.
It does NOT substitute the `ctypes documentation`_.
Please read the latter first if you have never called foreign functions with *ctypes* from *Python* scripts.

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
    memsync
    configuration

.. toctree::
    :maxdepth: 2
    :caption: Advanced

    interoperability
    wineenv
    benchmarks
    security
    bugs
    changes
    faq
    support

`Interested in contributing?`_

.. _Interested in contributing?: https://github.com/pleiszenburg/zugbruecke/blob/master/CONTRIBUTING.rst

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`
