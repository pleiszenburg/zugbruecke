:github_url:

.. _session:

.. index::
	single: zugbruecke.ctypes
	single: zugbruecke.ctypes_session

The session model
=================

*zugbruecke* operates based on a session model. Every session represents a separate *Windows* *Python* interpreter process running on *Wine*. *zugbruecke* starts a default session during the import of ``zugbruecke.ctypes``, but the user can start more sessions if required. Sessions are identified by a unique (hash) ID string. Sessions have a life-cycle and require termination routines to run before they can be dropped or deleted. By default, sessions terminate themselves automatically when the *Python* interpreter quits.

The following notable ``ctypes`` methods and classes and their functionality are linked to individual sessions and therefore depend on their internal state: ``cdll``, ``CDLL``, ``CFUNCTYPE``, ``windll``, ``WinDLL``, ``WINFUNCTYPE``, ``oledll``, ``OleDLL``, ``FormatError``, ``get_last_error``, ``GetLastError``, ``set_last_error`` and ``WinError``. In addition, the methods from ``ctypes.util``, i.e. ``find_library`` and ``find_msvcrt``, are also linked to individual sessions.

.. _sessionclass:

Class: ``zugbruecke.ctypes_session``
------------------------------------

By creating an instance of this class, a new session can be started. The number of instances/sessions is only (theoretically) limited by the amount of available memory and by the number of available network ports on the host system (two ports per instance are required). The :ref:`constructor can be configured <configconstructor>`.

Method: ``_zb_set_parameter``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parameters:

* ``parameter`` (dict)

Used to :ref:`re-configure <reconfiguration>` a running session. Accepts a dictionary containing :ref:`configuration parameters <configparameter>`.

Method: ``_zb_terminate``
^^^^^^^^^^^^^^^^^^^^^^^^^

This method can be used to manually terminate a session. It will quit the *Windows* *Python* interpreter running in the background. Once terminated, a session can not be re-started. Any handles on DLLs and their routines derived from this session will become useless.

String: ``_zb_id``
^^^^^^^^^^^^^^^^^^

Allows to read the unique session id.

Boolean: ``_zb_up``
^^^^^^^^^^^^^^^^^^^

Can be read to determine whether a session is up. Once a session is terminated, it will be set to ``False``.
