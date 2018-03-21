:github_url:

.. _session:

.. index::
	single: session
	single: current_session

The session model
=================

*zugbruecke* operates based on a session model. Every session represents
a separate *Windows* *Python* interpreter process running on *Wine*. By default,
*zugbruecke* starts one session during import, but the user can start more
sessions if required. Sessions are identified by a unique (hash) ID string.
Sessions have a life-cycle and require termination routines to run before
they can be dropped or deleted. By default, sessions terminate themselves
automatically when the *Python* interpreter quits.

.. _sessionclass:

Class: ``zugbruecke.session``
-----------------------------

By creating an instance of this class, a new session can be started. The number
of instances/sessions is only (theoretically) limited by the amount of available memory
and by the number of available network ports on the host system (two ports per
instance are required). The :ref:`constructor can be configured <configconstructor>`.

Method: ``load_library``
^^^^^^^^^^^^^^^^^^^^^^^^

Parameters:

* ``dll_name`` (str)
* ``dll_type`` (str)
* ``dll_param`` (dict, optional)

Return value:

* An instance of *zugbruecke*'s internal DLL representation, which mimics
  instances of *ctypes*' ``CDLL``, ``WinDLL`` or ``OleDLL`` classes depending on context.

The second parameter, ``dll_type``, determines the calling convention and can
be set to "cdll", "windll" or "oledll". Any other value will raise an error.

The first parameter, ``dll_name``, will be passed directly into the *ctypes*
library class constructor on the *Wine* side, i.e. ``CDLL``, ``WinDLL`` or ``OleDLL``.
All limitations and features of those constructors apply, e.g. the possibility
of referring to DLLs without their .dll-file-extension or the use of absolute
or relative *Windows* paths. *zugbruecke* offers :ref:`methods for path conversion <interoperability>`
if required. If *ctypes* on the *Wine* side raises an error, e.g. because the DLL
can not be found, the error will be re-raised by *zugbruecke* on the Unix side.

The third parameter is optional and allows to pass a dict with the following keys:

* ``mode``
* ``use_errno``
* ``use_last_error``

Those can be used to pass values into the corresponding parameters of the `ctypes constructors`_.

.. _ctypes constructors: https://docs.python.org/3/library/ctypes.html?highlight=ctypes#ctypes.CDLL

Method: ``set_parameter``
^^^^^^^^^^^^^^^^^^^^^^^^^

Parameters:

* ``parameter`` (dict)

Used to :ref:`re-configure <reconfiguration>` a running session. Accepts a dictionary
containing :ref:`configuration parameters <configparameter>`.

Method: ``terminate``
^^^^^^^^^^^^^^^^^^^^^

This method can be used to manually terminate a session. It will quit the
*Windows* *Python* interpreter running in the background. Once terminated, a session
can not be re-started. Any handles on DLLs and their routines derived from this
session will become useless.

String: ``id``
^^^^^^^^^^^^^^

Allows to read the unique session id.

Boolean: ``up``
^^^^^^^^^^^^^^^

Can be read to determine whether a session is up. Once a session is terminated,
it will be set to ``False``.

.. _currentsessionobject:

Instance: ``zugbruecke.current_session``
----------------------------------------

This is the default session of *zugbruecke*. It will be started during import.
Like every session, it can be :ref:`re-configured <reconfiguration>`
during run-time. If any of the usual *ctypes* members are imported from
*zugbruecke*, like for instance ``cdll``, ``CDLL``, ``CFUNCTYPE``, ``windll``, ``WinDLL``,
``WINFUNCTYPE``, ``oledll``, ``OleDLL``, ``FormatError``, ``get_last_error``, ``GetLastError``,
``set_last_error`` or ``WinError``, this session will be used.
