:github_url:

.. _FAQ:

FAQ
===

Why? Seriously, why?
--------------------

Good question. Have a look at the :ref:`motivation <motivation>` section in the introduction.

What are actual use cases for this project?
-------------------------------------------

Read the section on :ref:`use cases <usecases>` in the introduction.

How does it work?
-----------------

Have a closer look at the section describing the :ref:`implementation <implementation>` in the introduction.

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

Pointers to simple C data types (int, float, etc.) used as function parameters or within structures can be handled just fine.

Pointers to arbitrary data structures can be handled if another parameter of the call contains the length of the memory section the pointer is pointing to. *zugbruecke* uses a special ``memsync`` protocol for indicating which memory sections must be kept in sync between the *Unix* and the *Wine* side of the code. If run on *Windows*, the regular *ctypes* will just ignore any ``memsync`` directive in the code.

Is it thread-safe?
------------------

Probably (yes). More extensive tests are required.

If you want to be on the safe side, start one *zugbruecke* session per thread in your code manually. You can do this as follows:

.. code:: python

	from zugbruecke import ctypes_session
	# start new thread or process (multiprocessing) - then, inside, do:
	a = ctypes_session()
	# now you can do stuff like
	kernel32 = a.cdll.kernel32
	# do not forget to terminate the session (i.e. the Windows Python interpreter)
	a._zb_terminate()
