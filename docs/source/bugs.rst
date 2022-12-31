:github_url:

.. _bugs:

.. index::
	triple: bug; issue; report
	triple: bug; issue; bisect
	single: ctypes
	single: wine

Bugs & Known Issues
===================

Please report bugs in *zugbruecke* in *zugbruecke*'s `GitHub issue tracker`_.

Please report bugs in *ctypes* in the `Python tracker`_.

Please report bugs in *Wine* in the `WineHQ Bug Tracking System`_.

Make sure to separate between *zugbruecke*-related, *ctypes*-related and
*Wine*-related bugs.

.. _GitHub issue tracker: https://github.com/pleiszenburg/zugbruecke/issues
.. _Python tracker: https://github.com/python/cpython/issues
.. _WineHQ Bug Tracking System: https://bugs.winehq.org/

How to bisect issues
--------------------

*zugbruecke* is based on a :ref:`session model <session>`. Each session can be launched with parameters, which can either be passed into or picked up by the session constructor from a configuration file. It is also possible to change parameters during run-time.

If you want to increase the log level and/or enable writing of logs to disk during run-time, you can do the following:

.. code:: python

    import zugbruecke.ctypes as ctypes
    from logging import DEBUG
    ctypes.zb_set_parameter('log_level', DEBUG)
    ctypes.zb_set_parameter('log_write', True)
    # proceed as usual - with a lot more verbosity

A custom session can be manipulated in a similar way:

.. code:: python

    from zugbruecke import CtypesSession
    from logging import DEBUG
    ctypes = CtypesSession(log_level = DEBUG, log_write = True)
    # proceed as usual - with a lot more verbosity

Alternatively, you can drop a configuration file named ``.zugbruecke.json`` e.g. into your current working directory or your user account folder, ``/home/username``, and add configuration parameters to it, for example:

.. code:: json

    {"log_level": 10, "log_write": true}

.. note::

    The lower the log level, the more output you will get. *zugbruecke* used Python's ``logging`` module's log levels, see `logging documentation`_: ``DEBUG == 10``, ``INFO == 20``, ``WARNING == 30``, ``ERROR == 40`` and ``CRITICAL == 50``. Default is ``0`` for no logs as per ``NOTSET``.

The on-screen log is color-coded for readability. The log can also, in addition, be written to disk, where every log item with plenty of meta data is represented as a one-line JSON object for easy parsing and analysis of larger log files. For more configuration options check the :ref:`chapter on configuration <configuration>`.

.. _logging documentation: https://docs.python.org/3/howto/logging.html#logging-levels

As a last resort, you can activate additional debugging features intended for developers by setting the ``ZUGBRUECKE_DEBUG`` environment variable to ``1`` before importing ``zugbruecke`` or any component of it. For this to work, the `typeguard package`_ must be present on your system.

.. _typeguard package: https://typeguard.readthedocs.io/

As an alternative approach, you can also check what happens if you run your code directly in a *Windows Python* interpreter with *ctypes*. Consult the :ref:`chapter on the Wine Python environment <wineenv>` for details. It is easy to get *ctypes* syntax wrong, so this is a good approach for getting it right.

If in doubt, please also test your code with *ctypes* on an actual *Windows* system - it might be a bug in this module or *Wine* as well.

.. _centos:

Known issues: Running on CentOS
-------------------------------

.. warning::

    CentOS packages both CPython and Wine in rather unusual ways, effectively making it a minefield for *zugbruecke*. Avoid CentOS if possible.

*zugbruecke* expects the command for Wine 32 bit to be ``wine`` and the command for Wine 64 bit to be ``wine64``. This is not the case for CentOS' Wine packages where ``wine`` points to Wine 64 bit. However, alternative packages for CentOS restore the expected behaviour. For a discussion see `issue 70`_.

.. _issue 70: https://github.com/pleiszenburg/zugbruecke/issues/70

CentOS uses a customized CPython interpreter which behaves differently compared to a regular CPython interpreter. Notably, in regular builds of CPython, the authentication mechanism used by ``multiprocessing`` for connecting to other processes uses the MD5 hash algorithm by default, which is generally considered insecure. In CentOS, this mechanism was patched to use SHA256 for improved security. As a consequence, CentOS' CPython can not connect to an official Windows build of CPython, causing *zugbruecke* to fail to launch. A discussion and workarounds can be found in `issue 73`_.

.. _issue 73: https://github.com/pleiszenburg/zugbruecke/issues/73

*zugbruecke* is prone to random crashes during startup on older versions of CentOS. An ongoing discussion and a partial workaround can be found in `issue 78`_.

.. _issue 78: https://github.com/pleiszenburg/zugbruecke/issues/78
