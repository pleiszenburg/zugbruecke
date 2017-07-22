.. _FAQ:

FAQ
===

Why? Seriously, why?
--------------------

Good question. Have a look at the :ref:`motivation <motivation>` section in the introduction.

What are actual use cases for this project?
-------------------------------------------

Read the secion on :ref:`use cases <usecases>` in the introduction.

How does it work?
-----------------

During the first import of *zugbruecke*, a stand-alone *Windows*-version of the
*CPython* interpreter corresponding to the used *Unix*-version is automatically
downloaded and placed into the module's configuration folder (by default located at
``~/.zugbruecke/``). Next to it, also during first import, zugbruecke
generates its own *Wine*-profile directory for being used with a dedicated
``WINEPREFIX``. This way, any undesirable interferences with other *Wine*-profile
directories containing user settings and unrelated software are avoided.

During every import, *zugbruecke* starts the *Windows* *Python* interpreter on top of *Wine*.
It is used to run a server script named ``_server_.py``, located in the module's folder.

*zugbruecke* offers everything *ctypes* would on the *Unix* system it is running on
plus everything *ctypes* would offer if it was imported under *Windows*. Functions
and classes, which have a platform-specific behavior, are replaced with dispatchers.
The dispatchers decide whether the *Unix* or the *Windows* behavior should be used
depending on the context of how they were invoked and what parameters were passed
into them. If *Windows* specific behavior is chosen, calls are passed from
*zugbruecke*'s client code running on *Unix* to the server component of *zugbruecke*
running on *Wine*.

Is it secure?
-------------

No. See :ref:`chapter on security <security>`.

How fast/slow is it?
--------------------

It performs reasonably well. See :ref:`benchmark section <benchmarks>`.

Can it handle structures?
-------------------------

Yes, in principle. Though, limitations apply. See next question for details.

Can it handle pointers?
-----------------------

Yes and no.

Pointers to simple C data types (int, float, etc.) used as function
parameters or within structures can be handled just fine.

Pointers to arbitrary data structures can be handled if another parameter of
the call contains the length of the memory section the pointer is pointing to.
*zugbruecke* uses a special ``memsync`` protocol for indicating which memory
sections must be kept in sync between the *Unix* and the *Wine* side of the code.
If run on *Windows*, the regular *ctypes* will just ignore any ``memsync``
directive in the code.

Pointers returned by a DLL pointing to memory allocated by the DLL are
currently not handled. Null-terminated strings are not handled yet, too.

Is it thread-safe?
------------------

Probably (yes). More extensive tests are required.

If you want to be on the safe side, start one *zugbruecke* session per thread
in your code manually. You can do this as follows:

.. code:: python

	from zugbruecke import session
	# start new thread or process (multiprocessing) - then, inside, do:
	a = session()
	# now you can do stuff like
	kernel32 = a.load_library('kernel32', 'cdll')
	# do not forget to terminate the session (i.e. the Windows Python interpreter)
	a.terminate()
