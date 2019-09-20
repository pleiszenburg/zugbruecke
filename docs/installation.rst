:github_url:

.. _installation:

.. index::
	pair: pip; install
	triple: wine; linux; installation
	triple: wine; macos; installation
	triple: wine; bsd; installation

Installation
============

Getting *Wine*
--------------

For using *zugbruecke*, you need to install **Wine** first. Depending on your platform,
there are different ways of doing that.

* `Installation instructions for various Linux distributions`_
* `Installation instructions for Mac OS X`_
* `Installation instructions for FreeBSD`_

.. _Installation instructions for various Linux distributions: https://www.winehq.org/download
.. _Installation instructions for Mac OS X: https://wiki.winehq.org/MacOS
.. _Installation instructions for FreeBSD: https://wiki.winehq.org/FreeBSD

Currently, Wine >= 4.x is supported (tested). If you are limited to an older version of Wine such as 2.x or 3.x, you have two options: Try `an older version of this package`_ or try to set the ``pythonversion`` configuration parameter to ``3.5.4``.

.. _an older version of this package: https://github.com/pleiszenburg/zugbruecke/releases/tag/v0.0.14

Getting *zugbruecke*
--------------------

The latest (more or less) **stable release version** can be installed with *pip*:

.. code:: bash

	pip install zugbruecke

If you are interested in testing the latest work from the **development branch**, you can try it like this:

.. code:: bash

	pip install git+https://github.com/pleiszenburg/zugbruecke.git@develop

After installing the package with ``pip``, you may choose to manually initialize the "Wine Python environment" by running ``wenv init``. If you choose not to do this, ``zugbruecke`` will take care of it during its first use.

Possible problem: ``SSL/TSL has issues - please install "certifi" and try again``
---------------------------------------------------------------------------------

While running ``wenv init``, the command may terminate with a ``SystemExit`` exception entitled ``SSL/TSL has issues - please install "certifi" and try again``. This may happen on systems with older versions of ``libssl`` (``libopenssl``) or configuration issues regarding the SSL certificate store. You will most likely see additional information telling you that an SSL certificate could not be validated.

In most cases, a **clean solution** is to install ``certifi`` with pip: ``pip install -U certifi``. The ``-U`` option forces ``pip`` to update ``certifi`` if it is already installed. Once you have installed or updated ``certifi``, you can run ``wenv init`` again.

On known problematic systems, you may also choose to install ``zugbruecke`` directly with ``certifi`` included: ``pip install zugbruecke[certifi]``. Notice that this may have undesired security implications.

Possible problem: ``OSError: [WinError 6] Invalid handle``
----------------------------------------------------------

On older versions of Linux such as *Ubuntu 14.04* alias *Trusty Tahr* (released 2014), you may observe errors when running ``wenv python``. Most commonly, they will present themselves as ``OSError: [WinError 6] Invalid handle: 'z:\\...`` triggered by calling ``os.listdir`` in ``pip`` or ``importlib`` on folders related to ``zugbruecke``. You can easily test whether you are affected by this issue or not by running ``wenv python -c "import zugbruecke; print(dir(zugbruecke))"``. If you see the described ``OSError`` instead of meaningful output, you are affected.

A **clean solution** is to upgrade to a younger version of Linux. E.g. *Ubuntu 16.04* alias *Xenial Xerus* (released 2016) is known to work.

If upgrading Linux is not an option, there is a **less clean workaround**. Before running ``wenv init``, you can set the configuration option ``_issues_50_workaround`` to ``True``, see chapter on :ref:`configuration <configuration>`. If you have already initialized your *Wine Python environment* with ``wenv init``, you must remove it with ``wenv clean`` and then re-initialize it with ``wenv init``. Notice that - if you are using this workaround - removing your *Wine Python environment* with ``wenv clean`` and re-initializing it with ``wenv init`` is necessary after every update of ``zugbruecke``.

Installing *zugbruecke* in development mode
-------------------------------------------

If you are interested in contributing to *zugbruecke*, you might want to install it in
development mode. You can find the latest instructions on how to do this in the
`CONTRIBUTING file`_ of this project on *Github*.

.. _`CONTRIBUTING file`: https://github.com/pleiszenburg/zugbruecke/blob/master/CONTRIBUTING.rst
