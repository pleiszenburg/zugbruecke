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

Currently, Wine >= 4.x is supported. If you are limited to an older version of Wine such as 2.x or 3.x,
you will have to try `an older version of this package`_.

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

Possible problem: ``OSError: [WinError 6] Invalid handle``
----------------------------------------------------------

On older versions of Linux such as *Ubuntu 14.04* alias *Trusty Tahr* (released 2014), you may observe errors when running ``wenv python``. Most commonly, they will present themselves as ``OSError: [WinError 6] Invalid handle: 'z:\\...`` triggered by calling ``os.listdir`` in ``pip`` or ``importlib`` on folders related to ``zugbruecke``. You can easily test whether you are affected by this issue or not by running ``wenv python -c "import zugbruecke; print(dir(zugbruecke))"``. If you see the described ``OSError`` instead of meaningful output, you are affected.

A **clean solution** is to upgrade to a younger version of Linux. E.g. *Ubuntu 16.04* alias *Xenial Xerus* (released 2016) is known to work.

If upgrading Linux is not an option, there is a very **unclean workaround**. DO NOT FOLLOW THESE INSTRUCTIONS UNLESS YOU HAVE ABSOLUTELY NO OTHER OPTION. Typically, ``zugbruecke`` install its *Wine Python environment* into ``$HOME/.zugbruecke/win32-python3.X.Y/`` (where X and Y are the minor and micro versions of *Wine Python*). In ``$HOME/.zugbruecke/win32-python3.X.Y/Lib/site-packages`` you will find two symbolic links: ``zugbruecke`` and ``zugbruecke.egg-info``. They directly link to the corresponding folders in the ``site-packages`` directory of your *Unix Python* environment. Make a note of where the symbolic links are pointing to. Remove the symbolic links and substitute them with identically named folders. Copy the contents of ``site-packages/zugbruecke`` and ``zugbruecke/zugbruecke.egg-info`` in your *Unix Python environment* to their new counterparts in your *Wine Python environment*. Next, you have to open ``site-packages/zugbruecke/wenv.py`` from your *Unix Python environment*. Find the method ``ensure`` and remove/comment the ``self.setup_zugbruecke()`` instruction.

Installing *zugbruecke* in development mode
-------------------------------------------

If you are interested in contributing to *zugbruecke*, you might want to install it in
development mode. You can find the latest instructions on how to do this in the
`CONTRIBUTING file`_ of this project on *Github*.

.. _`CONTRIBUTING file`: https://github.com/pleiszenburg/zugbruecke/blob/master/CONTRIBUTING.rst
