:github_url:

.. _session:

.. index::
	single: zugbruecke.ctypes
	single: zugbruecke.ctypes_session

The session model
=================

*zugbruecke* operates based on a session model. Every session represents a separate *Windows* *Python* interpreter process running on *Wine*. *zugbruecke* starts a default session during the import of ``zugbruecke.ctypes``, but the user can start more sessions if required. Sessions are identified by a unique (hash) ID string. Sessions have a life-cycle and require termination routines to run before they can be dropped or deleted. By default, sessions terminate themselves automatically when the *Python* interpreter quits.

The following notable ``ctypes`` methods and classes and their functionality are linked to individual sessions and therefore depend on their internal state: ``cdll``, ``CDLL``, ``CFUNCTYPE``, ``windll``, ``WinDLL``, ``WINFUNCTYPE``, ``oledll``, ``OleDLL``, ``FormatError``, ``get_last_error``, ``GetLastError``, ``set_last_error`` and ``WinError``. In addition, the methods from ``ctypes.util``, i.e. ``find_library`` and ``find_msvcrt``, are also linked to individual sessions.

Working with sessions
---------------------

If you are just importing ``zugbruecke`` with ``import zugbruecke``, no session is started.

The default session is started if you import ``zugbruecke.ctypes`` with ``import zugbruecke.ctypes`` or if you import any sub-modules such as ``util`` with ``import zugbruecke.ctypes.util``. In most use-cases, you will not care about sessions. The default session is usually enough. It will automatically be terminated when the *Unix* *Python* interpreter stops running.

You may choose to run more than one session at a time for more advanced problems. For example, accessing different DLLs might require different session configurations for individual DLLs. Anther use case may be multithreading, where you might want to operate one session per thread.

.. _sessionclass:

Class: ``zugbruecke.ctypes_session``
------------------------------------

By creating an instance of this class, a new session can be started. The number of instances/sessions is only (theoretically) limited by the amount of available memory and by the number of available network ports on the host system (two ports per instance are required). The :ref:`constructor can be configured <configconstructor>`. The following example illustrates the life cycle of a session object:

.. code:: python

	from zugbruecke import ctypes_session
	session_a = ctypes_session()
	kernel32 = session_a.cdll.kernel32
	# do stuff with "kernel32" ...
	session_a._zb_terminate()

If you are using methods or classes, which depend on the internal state of a session, always use those connected to the relevant session, e.g.

.. code:: python

	from zugbruecke import ctypes_session
	session_a = ctypes_session()
	session_b = ctypes_session()
	kernel32 = session_a.cdll.kernel32
	msvcrt = session_b.cdll.msvcrt
	# do stuff with "kernel32" through "session_a" and "msvcrt" through "session_b" ...
	session_a._zb_terminate()
	session_b._zb_terminate()

Session configuration parameters can be altered through the session's constructor, for example:

.. code:: python

	from zugbruecke import ctypes_session
	session_64bit = ctypes_session(parameter = {'arch': 'win64'})
	session_32bit = ctypes_session(parameter = {'arch': 'win32'})

Notice that methods from the ``ctypes.util`` module are also depending on the internal state of a session. If you are working with custom sessions, DO NOT use the methods offered in ``zugbruecke.ctypes.util``. Instead, your custom session is offering a ``_util`` property:

.. code:: python

	from zugbruecke import ctypes_session
	session_a = ctypes_session()
	session_a._util.find_library('msvcrt.dll')
	session_b._zb_terminate()

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
