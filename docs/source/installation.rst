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

For using *zugbruecke*, you need to install **Wine** first. Depending on your platform, there are different ways of doing that.

* `Installation instructions for various Linux distributions`_
* `Installation instructions for Mac OS X`_
* `Installation instructions for FreeBSD`_

.. _Installation instructions for various Linux distributions: https://www.winehq.org/download
.. _Installation instructions for Mac OS X: https://wiki.winehq.org/MacOS
.. _Installation instructions for FreeBSD: https://wiki.winehq.org/FreeBSD

.. note::

	Currently, Wine >= 6.x is supported (tested).

.. warning::

    Calling into 32 bit DLLs requires a 32 bit version of *Wine*. As most Linux distributions have started to drop 32 bit support, 32 bit versions of *Wine* are now rarely shipped by default. On some Linux distributions, e.g. Ubuntu and derivatives, the installation of 32 bit packages must be explicitly activated before one can even attempt to install *Wine* for 32 bit. Please read related instructions for your Linux distribution carefully before proceeding.

.. warning::

	Support for Mac OS X and FreeBSD is provided on a best-effort basis. *zugbruecke* currently does not receive regular testing on those platforms.

Getting *zugbruecke*
--------------------

The latest (more or less) **stable release version** can be installed with *pip*:

.. code:: bash

	pip install zugbruecke

If you are interested in testing the latest work from the **development branch**, you can try it like this:

.. code:: bash

	pip install git+https://github.com/pleiszenburg/zugbruecke.git@develop

After installing the package with ``pip``, you may choose to manually :ref:`initialize the Wine Python environment <wineenv>` by running ``wenv init``. If you choose not to do this, ``zugbruecke`` will take care of it during its first use.

.. note::

	If you are relying on *zugbruecke*, please notice that it uses **semantic versioning**. Breaking changes are indicated by increasing the second version number, the minor version. Going for example from 0.0.x to 0.1.y or going from 0.1.x to 0.2.y therefore indicates a breaking change. For as long as *zugbruecke* has development status "alpha", please expect more breaking changes to come.

If you are encountering any problems, see :ref:`section on bugs and known issues <bugs>`.

Installing *zugbruecke* in Development Mode
-------------------------------------------

If you are interested in contributing to *zugbruecke*, you might want to install it in development mode. You can find the latest instructions on how to do this in the `CONTRIBUTING file`_ of this project on *Github*.

.. _`CONTRIBUTING file`: https://github.com/pleiszenburg/zugbruecke/blob/develop/CONTRIBUTING.md
