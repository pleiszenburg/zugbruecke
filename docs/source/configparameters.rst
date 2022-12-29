Configuration Strategy and Parameters
=====================================

Hierarchy
----------

*zugbruecke* retrieves configuration parameters from a number of places. It follows a hierarchy from highest to lowest *priority*, in the following order:

- Environment variables
- Keyword arguments provided by the user to the constructor of :class:`zugbruecke.CtypesSession`
- Configuration files
- Default values

.. warning::

    Environment variables are overwriting literally everything, including parameters passed directly into the *zugbruecke* session constructor!

Via Environment Variables
-------------------------

All configurable parameters of ``zugbruecke`` can directly be overridden with environment variables. Values from environment variables will always take precedence. Environment variables are named using a combination of the ``ZUGBRUECKE_`` prefix and the name of the parameter in question converted to upper case. The ``pythonversion`` could for instance be configured as follows: ``ZUGBRUECKE_PYTHONVERSION=3.7.9``

Via Files
---------

*zugbruecke* uses `JSON`_ configuration files. They are expected in the following locations, from highest to lowest priority:

.. _JSON: https://en.wikipedia.org/wiki/JSON

* file specified in the ``ZUGBRUECKE`` environment variable: ``{os.environ.get("ZUGBRUECKE")}``
* directory specified in the ``ZUGBRUECKE`` environment variable: ``{os.environ.get("ZUGBRUECKE")}/.zugbruecke.json``
* current working directory: ``{os.getcwd()}/.zugbruecke.json``
* user profile folder: ``{os.path.expanduser("~")}/.zugbruecke.json``
* ``etc`` folder: ``/etc/zugbruecke.json``
* ``etc`` folder (deprecated): ``/etc/.zugbruecke.json``
* ``etc`` folder: ``/etc/zugbruecke``

A configuration file may only deal with a subset of configuration parameters. For instance, a configuration file could only be used to specify a version of *Windows Python*:

.. code:: json

    {"pythonversion": "3.7.9"}

.. _configparameter:

Parameters
----------

The following parameters can be configured:

.. list-table::
    :header-rows: 1

    * - name
      - type
      - description
      - default
    * - id
      - ``str``
      - Unique, only configure it if necessary.
      - Random hash
    * - stdout
      - ``bool``
      - Show *Windows Python* ``stdout`` output.
      - ``True``
    * - stderr
      - ``bool``
      - Show *Windows Python* ``stderr`` output.
      - ``True``
    * - log_write
      - ``bool``
      - Write log to current working directory.
      - ``False``
    * - log_level
      - ``int``
      - Verbosity, from ``0`` to ``50``.
      - ``0``
    * - arch
      - ``str``
      - *Windows Python* architecture, ``win32`` or ``win64``.
      - ``win32``
    * - pythonversion
      - ``PythonVersion``
      - Version / build of *Windows Python*, >= 3.7.
      - ``3.7.4``
    * - timeout_start
      - ``int``
      - Wait seconds for *Windows Python* to show up.
      - ``30``
    * - timeout_stop
      - ``int``
      - Wait seconds for *Windows Python* to terminate.
      - ``30``
    * - copy_modules
      - ``bool``
      - Copy ``zugbruecke`` and ``wenv`` modules into wenv instead of symlink.
      - ``False``

.. note::

  (Only) ``log_level`` and ``log_write`` can be changed at run-time. ``log_level`` follows Python's ``logging`` module's log levels, i.e. ``DEBUG == 10``, ``INFO == 20``, ``WARNING == 30``, ``ERROR == 40`` and ``CRITICAL == 50``. Default is ``0`` for no logs as per ``NOTSET``.

.. note::

    ``pythonversion`` accepts ``wenv.PythonVersion`` objects, see `relevant section of wenv documentation`_. Version 3.6 and earlier are not supported. You can only specify versions / builds for which an "Windows embeddable zip file" is available, see `python.org`_ for details. ``wenv.get_available_python_builds`` (`see here`_) and ``wenv.get_latest_python_build`` (`also see here`_) can be used to automatically query available builds.

.. note::

    Next to the parameters listed above, *zugbruecke* also accepts every valid *wenv* configuration parameter and passes them on to *wenv* itself. See `relevant chapter of wenv documentation`_ for details.

.. _relevant section of wenv documentation: https://wenv.readthedocs.io/en/latest/pythonversion.html#wenv.PythonVersion
.. _relevant chapter of wenv documentation: https://wenv.readthedocs.io/en/latest/configuration.html#parameters
.. _python.org: https://www.python.org/downloads/windows/
.. _see here: https://wenv.readthedocs.io/en/latest/pythonversion.html#wenv.get_available_python_builds
.. _also see here: https://wenv.readthedocs.io/en/latest/pythonversion.html#wenv.get_latest_python_build
