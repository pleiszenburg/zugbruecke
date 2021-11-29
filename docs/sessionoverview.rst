.. _sessionoverview:

Working with Sessions
---------------------

Sessions are identified by a unique (hash) ID string. Sessions have a life-cycle and require termination routines to run before they can be dropped or deleted. By default, sessions terminate themselves automatically when the *Python* interpreter quits.

The following notable ``ctypes`` methods and classes and their functionality are linked to individual sessions and therefore depend on their internal state: ``cdll``, ``CDLL``, ``CFUNCTYPE``, ``windll``, ``WinDLL``, ``WINFUNCTYPE``, ``oledll``, ``OleDLL``, ``FormatError``, ``get_last_error``, ``GetLastError``, ``set_last_error`` and ``WinError``. In addition, the methods from ``ctypes.util``, i.e. ``find_library`` and ``find_msvcrt``, are also linked to individual sessions.

If you are just importing ``zugbruecke`` with ``import zugbruecke``, no session is started.

The default session is started if you import ``zugbruecke.ctypes`` with ``import zugbruecke.ctypes`` or if you import any sub-modules such as ``util`` with ``import zugbruecke.ctypes.util``. In most use-cases, you will not care about sessions. The default session is usually enough. It will automatically be terminated when the *Unix* *Python* interpreter stops running.

You may choose to run more than one session at a time for more advanced problems. For example, accessing different DLLs might require different session configurations for individual DLLs. Anther use case may be multithreading, where you might want to operate one session per thread.

.. warning::

	``ctypes.util`` is bound to a session ...

By creating an instance of this class, a new session can be started. The number of instances/sessions is only (theoretically) limited by the amount of available memory and by the number of available network ports on the host system (two ports per instance are required). The following example illustrates the life cycle of a session object:

.. code:: python

	from zugbruecke import CtypesSession
	session_a = CtypesSession()
	kernel32 = session_a.cdll.kernel32
	# do stuff with "kernel32" ...
	session_a._zb_terminate()

If you are using methods or classes, which depend on the internal state of a session, always use those connected to the relevant session, e.g.

.. code:: python

	from zugbruecke import CtypesSession
	session_a = CtypesSession()
	session_b = CtypesSession()
	kernel32 = session_a.cdll.kernel32
	msvcrt = session_b.cdll.msvcrt
	# do stuff with "kernel32" through "session_a" and "msvcrt" through "session_b" ...
	session_a._zb_terminate()
	session_b._zb_terminate()

Session configuration parameters can be altered through the session's constructor, for example:

.. code:: python

	from zugbruecke import CtypesSession
	session_64bit = CtypesSession(parameter = {'arch': 'win64'})
	session_32bit = CtypesSession(parameter = {'arch': 'win32'})

Notice that methods from the ``ctypes.util`` module are also depending on the internal state of a session. If you are working with custom sessions, DO NOT use the methods offered in ``zugbruecke.ctypes.util``. Instead, your custom session is offering a ``_util`` property:

.. code:: python

	from zugbruecke import CtypesSession
	session_a = CtypesSession()
	session_a._util.find_library('msvcrt.dll')
	session_b._zb_terminate()
