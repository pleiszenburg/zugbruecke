.. _sessionoverview:

Working with Sessions
=====================

Overview
--------

One session wraps a exactly one *Windows Python* process on top of *Wine*. The session essentially manages the process and takes care of communication between it and the "host" *Unix Python* process. ``ctypes`` API calls are routed from the *Unix Python* process into the *Windows Python* process and executed there. Where applicable, memory content is being kept in sync between both processes, either automatically or via :ref:`user defined directives <memsync>`.

*zugbruecke* offers two primary ways of working with sessions. If ``zugbruecke.ctypes`` is being imported, it can be used directly as if regular ``ctypes`` was imported instead. A *default session* is being created and configured automatically in the background. This also applies to importing ``zugbruecke.ctypes.util``. Alternatively, *ctypes sessions*, instances of :class:`zugbruecke.CtypesSession`, can also be created and :ref:`configured <configuration>` on demand as needed.

.. note::

	If you are just importing ``zugbruecke`` with ``import zugbruecke``, no session is started.

Sessions are identified by a *unique ID string*. By default, this is a random hash value. However, it can also be set at the time of session creation. The ID is prominently shown in logging / debugging output of *zugbruecke*.

Sessions have a *life-cycle* and require termination routines to run before they can be dropped or deleted.

.. note::

	By default, sessions terminate themselves automatically when the *Unix Python* interpreter quits.

Certain ``ctypes`` functionality is *bound* to an individual session and its internal state.

Bound, Stable Functions and Classes
-----------------------------------

The following notable ``ctypes`` functions and classes and their functionality are bound to individual sessions and therefore depend on their internal state:

- ``CDLL`` and ``cdll``
- ``WinDLL`` and ``windll``
- ``CFUNCTYPE`` and ``WINFUNCTYPE``

In addition, the functions from ``ctypes.util`` are also bound to individual sessions:

- ``find_library``
- ``find_msvcrt``

Untested, Bound Functions and Classes
-------------------------------------

The following functions are bound to sessions and implemented, but untested and provided on a best-effort basis:

- ``OleDLL`` and ``oledll``
- ``FormatError``
- ``get_last_error``
- ``GetLastError``
- ``set_last_error``
- ``WinError``

Bound Stubs and Unimplemented Functionality
-------------------------------------------

*zugbruecke* currently does not support every *ctypes* feature. The following noteworthy functions and classes are only provided as stubs and raise ``NotImplementedError`` if called:

- ``PyDLL`` and ``pydll``
- ``DllCanUnloadNow``
- ``DllGetClassObject``
- ``HRESULT``

Special APIs
------------

Every *zugbruecke* session offers a number of special APIs for session management, prefixed with ``zb_``:

- ``__repr__``
- ``__enter__``
- ``__exit__``
- ``zb_get_parameter``
- ``zb_set_parameter``
- ``zb_terminate``
- ``zb_id``
- ``zb_client_up``
- ``zb_server_up``
- ``zb_path_unix_to_wine``
- ``zb_path_wine_to_unix``

Session Lifecycle
-----------------

Every *zugbruecke* session or, to be more precise, every *Windows Python* process on top of *Wine*, has a lifecycle and needs to be terminated. By default, sessions are automatically terminated when the *Unix Python* process quits.

Sessions are started by creating an instance of :class:`zugbruecke.CtypesSession`. The following example illustrates the life cycle of a session object:

.. code:: python

	from zugbruecke import CtypesSession
	ctypes = CtypesSession() # session creation

	kernel32 = ctypes.cdll.kernel32
	# do stuff with "kernel32" ...

	ctypes.zb_terminate() # session termination

Sessions can also be conveniently managed via Python's context managers:

.. code:: python

	from zugbruecke import CtypesSession

	with CtypesSession() as ctypes: # session creation AND termination
		kernel32 = ctypes.cdll.kernel32
		# do stuff with "kernel32" ...

The *default session* can of cause also be terminated:

.. code:: python

	from zugbruecke import ctypes # session creation

	kernel32 = ctypes.cdll.kernel32
	# do stuff with "kernel32" ...

	ctypes.zb_terminate() # session termination

A session's "health status" can be inspected via two of its properties:

.. code:: python

	from zugbruecke import CtypesSession
	ctypes = CtypesSession() # session creation

	assert ctypes.zb_client_up
	assert ctypes.zb_server_up

	ctypes.zb_terminate() # session termination

	assert not ctypes.zb_client_up
	assert not ctypes.zb_server_up

Both, ``zb_client_up`` and ``zb_server_up``, are supposed to be ``True`` if the session is up and running and should both be ``False`` is the session has been correctly terminated.

Parallel Sessions
-----------------

You may choose to run more than one session at a time for more advanced problems. For example, accessing 32 bit and 64 bit DLLs simultaneously requires different session configurations for ``win32`` and ``win64`` architectures. Anther use case may be multithreading, where you might want to operate one session per thread. The number of sessions is only (theoretically) limited by the amount of available memory and by the number of available network ports on the host system (two ports per instance are required).

If you are using functions or classes, which are bound to a session, always use those connected to the relevant session, e.g.

.. code:: python

	from zugbruecke import CtypesSession

	ctypes_a = CtypesSession() # session creation
	ctypes_b = CtypesSession() # session creation

	assert ctypes_a.zb_id != ctypes_b.zb_id

	kernel32 = ctypes_a.cdll.kernel32
	msvcrt = ctypes_b.cdll.msvcrt
	# do stuff with "kernel32" through "ctypes_a"
	# do stuff with "msvcrt" through "ctypes_b"

	ctypes_a.zb_terminate() # session termination
	ctypes_b.zb_terminate() # session termination

Configuring Sessions
--------------------

Session configuration parameters can be altered in multiple ways. For details on configuration options, see :ref:`chapter on configuration <configuration>`. First, a session can be configured at the time of its creation by passing a :class:`zugbruecke.Config` object with custom options into it:

.. code:: python

	from zugbruecke import CtypesSession, Config

	ctypes_32bit = CtypesSession(Config(arch = "win32")) # for 32 bit DLLs
	ctypes_64bit = CtypesSession(Config(arch = "win64")) # for 64 bit DLLs

Second, a session can be reconfigured during run-time. However, very few parameters can actually be changed once a session has been created. Consider the following example:

.. code:: python

	from zugbruecke import CtypesSession

	ctypes = CtypesSession()

	assert ctypes.zb_get_parameter('log_level') == 0
	ctypes.zb_set_parameter('log_level', 100)
	assert ctypes.zb_get_parameter('log_level') == 100
