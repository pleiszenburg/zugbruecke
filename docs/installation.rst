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

Currently, Wine >= 6.x is supported (tested).

Getting *zugbruecke*
--------------------

The latest (more or less) **stable release version** can be installed with *pip*:

.. code:: bash

	pip install zugbruecke

If you are interested in testing the latest work from the **development branch**, you can try it like this:

.. code:: bash

	pip install git+https://github.com/pleiszenburg/zugbruecke.git@develop

After installing the package with ``pip``, you may choose to manually initialize the "Wine Python environment" by running ``wenv init``. If you choose not to do this, ``zugbruecke`` will take care of it during its first use.

If you are relying on *zugbruecke*, please notice that it uses semantic versioning. Breaking changes are indicated by increasing the second version number, the minor version. Going for example from 0.0.x to 0.1.0 or going from 0.1.y to 0.2.0 therefore indicates a breaking change. For as long as *zugbruecke* has development status "alpha", please expect more breaking changes to come.

Possible problem: ``SSL/TSL has issues - please install "certifi" and try again``
---------------------------------------------------------------------------------

While running ``wenv init``, the command may terminate with a ``SystemExit`` exception entitled ``SSL/TSL has issues - please install "certifi" and try again``. This may happen on systems with older versions of ``libssl`` (``libopenssl``) or configuration issues regarding the SSL certificate store. You will most likely see additional information telling you that an SSL certificate could not be validated.

In most cases, a **clean solution** is to install ``certifi`` with pip: ``pip install -U certifi``. The ``-U`` option forces ``pip`` to update ``certifi`` if it is already installed. Once you have installed or updated ``certifi``, you can run ``wenv init`` again.

On known problematic systems, you may also choose to install ``zugbruecke`` directly with ``certifi`` included: ``pip install zugbruecke[certifi]``. Notice that this may have undesired security implications.

Installing *zugbruecke* in development mode
-------------------------------------------

If you are interested in contributing to *zugbruecke*, you might want to install it in
development mode. You can find the latest instructions on how to do this in the
`CONTRIBUTING file`_ of this project on *Github*.

.. _`CONTRIBUTING file`: https://github.com/pleiszenburg/zugbruecke/blob/master/CONTRIBUTING.rst
