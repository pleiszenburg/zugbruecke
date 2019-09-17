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

Getting *zugbruecke*
--------------------

The latest (more or less) **stable release version** can be installed with *pip*:

.. code:: bash

	pip install zugbruecke

If you are interested in testing the latest work from the **development branch**, you can try it like this:

.. code:: bash

	pip install git+https://github.com/pleiszenburg/zugbruecke.git@develop

After installing the package with ``pip``, you may choose to manually initialize the "Wine Python environment" by running ``wenv init``. If you choose not to do this, ``zugbruecke`` will take care of it during its first use.

Installing *zugbruecke* in development mode
-------------------------------------------

If you are interested in contributing to *zugbruecke*, you might want to install it in
development mode. You can find the latest instructions on how to do this in the
`CONTRIBUTING file`_ of this project on *Github*.

.. _`CONTRIBUTING file`: https://github.com/pleiszenburg/zugbruecke/blob/master/CONTRIBUTING.rst
