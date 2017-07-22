.. _memsync:

.. index::
	single: pointer

Handling pointers
=================

The memory synchronization protocol
-----------------------------------

Because *zugbruecke* runs core in a separate *Python* interpreter on *Wine*,
pointers pose a special kind of problem. The can, unfortunately, not be passed
from the code running on the *Unix* side to the code running on the *Wine* side
or vice versa. This is why the memory pointers are pointing to must be kept in
sync on both sides. The memory synchronization can be controlled by the user
through the ``memsync`` protocol. ``memsync`` implements special directives,
which do not interfere with *ctypes* should the code be required to run on
*Windows* as well.

A simple example
----------------

Consider the following example DLL routine in C:

.. code:: C

	/* Average values in an array */
	void __stdcall __declspec(dllimport) bubblesort(
		float *a,
		int n
		)
	{
		int i, j;
		for (i = 0; i < n - 1; ++i)
		{
			for (j = 0; j < n - i - 1; ++j)
			{
				if (a[j] > a[j + 1])
				{
					float tmp = a[j];
					a[j] = a[j + 1];
					a[j + 1] = tmp;
				}
			}
		}
	}

It is a really simple implementation of the "bubblesort" algorithm, which accepts
a pointer to an array of floats of arbitrary length and an integer with length information.
The array is being sorted within its own memory, so the caller expects a sorted
array at the passed pointer after the call.

With *ctypes* on *Windows*, you could call it like this:

.. code:: python

	from ctypes import windll, cast, pointer, POINTER, c_float, c_int

	__dll__ = windll.LoadLibrary('demo_dll.dll')
	__bubblesort__ = __dll__.bubblesort
	__bubblesort__.argtypes = (POINTER(c_float), c_int)

	def bubblesort(values):

		ctypes_float_values = ((c_float)*len(values))(*values)
		ctypes_float_pointer_firstelement = cast(
			pointer(ctypes_float_values), POINTER(c_float)
			)
		__bubblesort__(ctypes_float_pointer_firstelement, len(values))
		values[:] = ctypes_float_values[:]

	test_vector = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
	bubblesort(test_vector)

For running the same code with *zugbruecke* on *Unix*, you need to add
information on the memory segment representing the array. This is done by
adding another attribute, ``memsync``, to the ``__bubblesort__`` function handle
(just like you usually specify ``argtypes`` and/or ``restype``). The following
example demonstrates how you must modify the above example so it works with
*zugbruecke*:

.. code:: python

	from zugbruecke import windll, cast, pointer, POINTER, c_float, c_int

	__dll__ = windll.LoadLibrary('demo_dll.dll')
	__bubblesort__ = __dll__.bubblesort
	__bubblesort__.argtypes = (POINTER(c_float), c_int)
	__bubblesort__.memsync = [
		{
			'p': [0],
			'l': [1],
			'_t': c_float
			}
		]

	def bubblesort(values):

		ctypes_float_values = ((c_float)*len(values))(*values)
		ctypes_float_pointer_firstelement = cast(
			pointer(ctypes_float_values), POINTER(c_float)
			)
		__bubblesort__(ctypes_float_pointer_firstelement, len(values))
		values[:] = ctypes_float_values[:]

	test_vector = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
	bubblesort(test_vector)

Two things have changed. First, the import statement turned from *ctypes* to
*zugbruecke*, although the exact same types, routines and objects were imported.
Second, ``__bubblesort__`` received an additional ``memsync`` attribute.

Because the ``memsync`` attribute will be ignored by *ctypes*, you can make the
above piece of code platform-independent by adjusting the import statement only.
The complete example, which will run on *Unix* and on *Windows* looks just like this:

.. code:: python

	from sys import platform
	if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:
		from zugbruecke import windll, cast, pointer, POINTER, c_float, c_int
	elif platform.startswith('win'):
		from ctypes import windll, cast, pointer, POINTER, c_float, c_int
	else:
		raise # handle other platforms here

	__dll__ = windll.LoadLibrary('demo_dll.dll')
	__bubblesort__ = __dll__.bubblesort
	__bubblesort__.argtypes = (POINTER(c_float), c_int)
	__bubblesort__.memsync = [
		{
			'p': [0],
			'l': [1],
			'_t': c_float
			}
		]

	def bubblesort(values):

		ctypes_float_values = ((c_float)*len(values))(*values)
		ctypes_float_pointer_firstelement = cast(
			pointer(ctypes_float_values), POINTER(c_float)
			)
		__bubblesort__(ctypes_float_pointer_firstelement, len(values))
		values[:] = ctypes_float_values[:]

	test_vector = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
	bubblesort(test_vector)

Attribute: ``memsync`` (list of dict)
----------------------------------------

``memsync`` is a list of dictionaries. Every dictionary represents one memory
section, which must be kept in sync. It has the following keys:

* ``p`` (:ref:`path to pointer <pathpointer>`)
* ``l`` (:ref:`path to length <pathlength>`)
* ``_c`` (optional)
* ``_t``

.. _pathpointer:

Path to pointer ``p`` (list of int and/or str)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This parameter describes where in the arguments (along the lines of ``argtypes``)
*zugbruecke*'s parser can find the pointer, which it is expected to handle.
Consider the following example:

.. code:: python

	# arg nr:    0        1        2
	some_routine(param_a, param_b, param_c)

If ``param_b`` was the pointer, ``p`` would be ``[1]`` (a list with a single int),
referring to the second argument of ``some_routine`` (counted from zero).

The following more complex example illustrates why ``p`` is a list actually
representing something like a "path":

.. code:: python

	class some_struct(Structure):
		_fields_ = [
			('field_a', POINTER(c_float)),
			('field_b', c_int)
			]

	# arg nr:          0        1        2        3
	some_other_routine(param_a, param_b, param_c, param_d)

Let's assume that ``param_a`` is of type ``some_struct`` and ``field_a`` contains
the pointer. ``p`` would look like this: ``[0, 'field_a']``. The pointer is found
in ``field_a`` of the first parameter of ``some_other_routine``, ``param_a``.
You should be able to extrapolate from here.

.. _pathlength:

Path to length ``l`` (list of int and/or str)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This parameter works just like the :ref:`path to pointer <pathpointer>` parameter.
It is expected to tell the parser, where it can find a number (int) which represents
the length of the memory block.
