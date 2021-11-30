:github_url:

.. _configuration:

.. index::
    pair: python; version
    triple: python; arch; architecture
    triple: wine; arch; architecture
    triple: log; level; write
    statement: zugbruecke.ctypes._zb_set_parameter
    module: zugbruecke.core.config

Configuration
=============

*zugbruecke* can automatically configure itself or can be configured manually. The configuration allows you to fine-tune its verbosity, architecture and other relevant parameters on a per-session basis. By importing ``zugbruecke.ctypes``, a default session is started and configured automatically. Alternatively, you can create and configure your own sessions manually by creating instances of :class:`zugbruecke.CtypesSession`. See the :ref:`chapter on the session model <session>` for details. Sessions can be configured :ref:`at the time of their creation <configconstructor>` as well as :ref:`at run-time <reconfiguration>`.

Configuration Files
-------------------

*zugbruecke* uses ``JSON`` configuration files named ``.zugbruecke.json``. They are expected in the following locations (in that order):

* The current working directory
* A directory specified in the ``ZUGBRUECKE`` environment variable
* The *zugbruecke* root directory (``~/.zugbruecke`` by default)
* ``/etc/zugbruecke``

There are two optional additions to the above rules: ``/etc/zugbruecke`` and the path specified in the ``ZUGBRUECKE`` environment variable can directly point to a configuration file. I.e. ``zugbruecke`` can also be a file in ``/etc/`` and the ``ZUGBRUECKE`` environment variable can also contain a path similar ``/path/to/some/file.json``.

Parameters passed directly into the *zugbruecke* session constructor will always be given priority. Beyond that, missing parameters are being looked for location after location in the above listed places. If, after checking for configuration files in all those locations, there are still parameters left undefined, *zugbruecke* will fill them with its defaults. A parameter found in a location higher in the list will always be given priority over a the same parameter with different content found in a location further down the list.

Configuration Environment Variables
-----------------------------------

Independently of the ``ZUGBRUECKE`` environment variable, all configurable parameters of ``zugbruecke`` can directly be overridden with environment variables. All values coming from configuration files as well as re-configurations at run-time will then be ignored for this particular parameter. Take the name of any configurable parameter, convert it to upper case and prefix it with ``ZUGBRUECKE``. Example: The ``arch`` parameter can be overridden by declaring the ``ZUGBRUECKE_ARCH`` environment variable.

.. _configparameter:

Configuration Parameters
------------------------

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
      - Verbosity, from ``0`` to ``100``.
      - ``0``
    * - arch
      - ``str``
      - *Windows Python* architecture, ``win32`` or ``win64``.
      - ``win32``
    * - pythonversion
      - ``str``
      - Version / build of *Windows Python*, >= 3.6.
      - ``3.7.4``
    * - timeout_start
      - ``int``
      - Wait seconds for *Windows Python* to show up.
      - ``30``
    * - timeout_stop
      - ``int``
      - Wait seconds for *Windows Python* to terminate.
      - ``30``

.. warning::

    Currently, only ``log_level`` can be changed at run-time.

.. note::

	Please note that 3.5 and earlier are not supported. Note that you can only specify versions for which an "Windows embeddable zip file" is available, see `python.org`_.

.. _python.org: https://www.python.org/downloads/windows/

The ``zugbruecke.Config`` class
-------------------------------

.. autoclass:: zugbruecke.Config
    :members:
