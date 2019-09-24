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

*zugbruecke* can configure itself or can be configured with files or can be (re-) configured during run-time. The configuration allows you to fine-tune its verbosity, architecture and other relevant parameters on a per-session basis.

By importing ``zugbruecke.ctypes``, a default session is started and configured automatically. Alternatively, you can create and configure your own sessions manually with ``zugbruecke.ctypes_session()``. See the :ref:`chapter on the session model <session>` for details.

.. _configconstructor:

Configuring the session constructor
-----------------------------------

If you chose to start your own session with ``zugbruecke.ctypes_session()``, the session constructor can be provided with a dictionary containing parameters.

Configuration files
-------------------

*zugbuecke* uses ``JSON`` configuration files named ``.zugbruecke.json``. They are expected in the following locations (in that order):

* The current working directory
* A directory specified in the ``ZUGBRUECKE`` environment variable
* The *zugbuecke* root directory (``~/.zugbruecke`` by default)
* ``/etc/zugbruecke``

There are two optional additions to the above rules: ``/etc/zugbruecke`` and the path specified in the ``ZUGBRUECKE`` environment variable can directly point to a configuration file. I.e. ``zugbruecke`` can also be a file in ``/etc/`` and the ``ZUGBRUECKE`` environment variable can also contain a path similar ``/path/to/some/file.json``.

Parameters passed directly into the *zugbuecke* session constructor will always be given priority. Beyond that, missing parameters are being looked for location after location in the above listed places. If, after checking for configuration files in all those locations, there are still parameters left undefined, *zugbuecke* will fill them with its defaults. A parameter found in a location higher in the list will always be given priority over a the same parameter with different content found in a location further down the list.

Configuration environment variables
-----------------------------------

Independently of the ``ZUGBRUECKE`` environment variable, all configurable parameters of ``zugbruecke`` can directly be overridden with environment variables. All values coming from configuration files as well as re-configurations at run-time will then be ignored for this particular parameter. Take the name of any configurable parameter, convert it to upper case and prefix it with ``ZUGBRUECKE``. Example: The ``arch`` parameter can be overridden by declaring the ``ZUGBRUECKE_ARCH`` environment variable.

.. _reconfiguration:

Re-configuration of a session during run-time
---------------------------------------------

Every session exposes a ``_zb_set_parameter`` method, which accepts a key (parameter name) and a value (parameter). Every session exposes also a ``_zb_get_parameter`` method, which accepts a key (parameter name) and returns a value (parameter).

.. code:: python

	import os
	import zugbruecke.ctypes as ctypes
	ctypes._zb_set_parameter('wineprefix', os.path.join(ctypes._zb_get_parameter('dir'), 'test-wineprefix'))
	# [proceed with using zugbruecke ...]

Investigating the environment's configuration
---------------------------------------------

*zugbruecke* exposes a dictionary-like class named ``config``. It can be used to investigate the available configuration as it is perceived by *zugbruecke* - without requiring to start a session. It can also be useful for deriving custom parameters at runtime.

.. code:: python

	import os
	import zugbruecke
	demo_session = zugbruecke.ctypes_session(parameter = {'wineprefix': os.path.join(zugbruecke.config()['dir'], 'test-wineprefix')})
	# [proceed with using zugbruecke ...]

.. _configparameter:

Configurable parameters
-----------------------

``id`` (str)
^^^^^^^^^^^^

Every *zugbuecke* ``session`` has a unique ``id``, which allows easier debugging and keeping track of multiple simultaneously running sessions. If no session id is provided by the user, *zugbuecke* will automatically generate a random hash ``string`` for every new session. Only manually configure this if absolutely necessary.

``stdout`` (bool)
^^^^^^^^^^^^^^^^^

Tells *zugbuecke* to show messages its sub-processes are writing to ``stdout``. ``True`` by default.

``stderr`` (bool)
^^^^^^^^^^^^^^^^^

Tells *zugbuecke* to show messages its sub-processes are writing to ``stderr``. ``True`` by default.

``log_write`` (bool)
^^^^^^^^^^^^^^^^^^^^

Tells *zugbuecke* to write its logs to disk into the current working directory. ``False`` by default.

``log_level`` (int)
^^^^^^^^^^^^^^^^^^^

Changes the verbosity of *zugbuecke*. ``0`` for no logs, ``10`` for maximum logs. ``0`` by default.

``arch`` (str)
^^^^^^^^^^^^^^

Defines the architecture of *Wine* & *Wine* *Python*. It can be set to ``win32`` or ``win64``. Default is ``win32``, even on 64-bit systems. It appears to be a more stable configuration.

``dir`` (str)
^^^^^^^^^^^^^

This parameter defines the root directory of *zugbruecke*. This is where by default *zugbruecke*'s own *Wine* profile folder is stored (``WINEPREFIX``) and where the :ref:`Wine Python environment <wineenv>` resides. By default, it is set to ``~/.zugbruecke``.

``pythonversion`` (str)
^^^^^^^^^^^^^^^^^^^^^^^

The ``pythonversion`` parameter tells *zugbuecke* what version of the *Windows* *CPython* interpreter it should use. By default, it is set to ``3.7.4``.

Please note that 3.4 and earlier are not supported. In the opposite direction, at the time of writing, 3.6 (and later) do require Wine 4.0 or later. If you are forced to use *Wine* 2.0 or 3.0, you may try to set this parameter to ``3.5.4``. Note that you can only specify versions for which an "Windows embeddable zip file" is available, see `python.org`_.

.. _python.org: https://www.python.org/downloads/windows/

``pythonprefix`` (str)
^^^^^^^^^^^^^^^^^^^^^^^

This parameter can be used to specify a custom location for the *Wine Python environment* outside of ``dir`` if required.

``timeout_start`` (integer)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Defines how many seconds *zugbruecke* waits for the *Windows* *CPython* interpreter to show up. A ``TimeoutError`` is raised if more time elapses. By default, it is set to 30 seconds.

``timeout_stop`` (integer)
^^^^^^^^^^^^^^^^^^^^^^^^^^

Defines how many seconds *zugbruecke* waits for every individual step of the termination routine of the *Windows* *CPython* interpreter. A ``TimeoutError`` is raised if the interpreter can not be terminated. By default, it is set to 30 seconds.

``wineprefix`` (str)
^^^^^^^^^^^^^^^^^^^^

This parameter can be used to point to a custom ``WINEPREFIX`` outside of ``dir`` if desired.

``winedebug`` (str)
^^^^^^^^^^^^^^^^^^^

*Wine* allows to control the level of debugging output through the ``WINEDEBUG`` environment variable. *zugbruecke* will by default disable all output by setting it to ``-all``. A custom value can be specified in the ``winedebug`` configuration parameter.
