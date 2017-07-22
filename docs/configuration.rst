.. _configuration:

.. index::
	pair: python; version
	triple: python; arch; architecture
	triple: wine; arch; architecture
	triple: log; level; write
	statement: zugbruecke.current_session.set_parameter
	module: zugbruecke.core.config

Configuration
=============

*zugbruecke* can configure itself or can be configured with files or can
be (re-) configured during run-time. The configuration allows you to fine-tune
its verbosity, architecture and other relevant parameters.

Configuration files
-------------------



Configurable parameters
-----------------------

``id`` (str)
^^^^^^^^^^^^

Every *zugbuecke* ``session`` has a unique ``id``, which allows easier debugging
and keeping track of multiple simultaneously running sessions. If no session
id is provided by the user, *zugbuecke* will automatically generate a random
hash ``string`` for every new session. Only manually configure this if absolutely
necessary.

``stdout`` (bool)
^^^^^^^^^^^^^^^^^

Tells *zugbuecke* to show messages its sub-processes write to ``stdout``.
``True`` by default.

``stderr`` (bool)
^^^^^^^^^^^^^^^^^

Tells *zugbuecke* to show messages its sub-processes write to ``stderr``.
``True`` by default.

``logwrite`` (bool)
^^^^^^^^^^^^^^^^^^^

Tells *zugbuecke* to write its logs to disk into the current working directory.
``False`` by default.

``log_level`` (int)
^^^^^^^^^^^^^^^^^^^

Changes the verbosity of *zugbuecke*. ``0`` for no logs, ``10`` for maximum logs.
``0`` by default.

``arch`` (str)
^^^^^^^^^^^^^^

Defines the architecture of Wine & Wine Python. It can be set to ``win32`` or ``win64``.
Default is ``win32``, even on 64-bit systems. It appears to be a more stable configuration.

``version`` (str)
^^^^^^^^^^^^^^^^^

The ``version`` parameter tells *zugbuecke* what version of the Windows CPython interpreter
it should use. By default, it is set to ``3.5.3``.

Please not that 3.4 and earlier are not supported. In the opposite direction, at the time of
writing, 3.6 (and later) does not work under Wine due to a `bug in Wine`_.

.. _bug in Wine: https://github.com/pleiszenburg/zugbruecke/issues/13

``dir`` (str)
^^^^^^^^^^^^^

This parameter defines the root directory of *zugbruecke*. It is where *zugbruecke*'s
own *Wine* profile folder is stored (``WINEPREFIX``) and where the Wine Python environment
resides. By default, it is set to ``~/.zugbruecke``.
