The ``memsync`` attribute
=========================

``memsync`` must be of type ``list[dict]``, i.e. a list of dictionaries. Each dictionary represents one memory section, which must be kept in sync. It can have the following keys:

* ``p`` (:ref:`path to pointer <pathpointer>`)
* ``l`` (:ref:`path to length <pathlength>`, optional)
* ``n`` (:ref:`NULL-terminated string flag <nullstring>`, optional)
* ``w`` (:ref:`Unicode character flag <unicodechar>`, optional)
* ``t`` (:ref:`data type of pointer <pointertype>`, optional)
* ``f`` (:ref:`custom length function <length function>`, optional)
* ``_c`` (:ref:`custom data type <customtype>`, optional)

Paths
-----

``memsync`` describes items within function arguments and return values based on "paths". Consider the following example:

.. code:: python

	# arg index: 0        1        2
	some_routine(param_a, param_b, param_c)

If ``param_b`` was the item in question, its path would be ``[1]``, a list with a single integer, referring to the second argument of ``some_routine`` counted from zero.

The following more complex example illustrates why the list is actually representing something like a "path":

.. code:: python

	class some_struct(Structure):
		_fields_ = [
			('field_a', POINTER(c_float)),
			('field_b', c_int),
		]

	# arg index:       0        1        2        3
	some_other_routine(param_a, param_b, param_c, param_d)

Let's assume that ``param_a`` is of type ``some_struct`` and ``field_a`` contains the target item. The path would look as follows: ``[0, 'field_a']``. The target item is found in ``field_a`` of the first parameter of ``some_other_routine`` counted from zero, ``param_a``.

Return values or elements within can be targeted by setting the first element of a path to ``'r'``, instead of an integer targeting an argument.

.. _pathpointer:

Key: ``p``, path to pointer
---------------------------

- Type: ``list[str | int]``

This parameter describes where *zugbruecke*'s parser can find the pointer, which it is expected to handle.

.. _pathlength:

Key: ``l``, path to length
--------------------------

- Type: ``list[str | int] | tuple[list[str | int]]``
- Optional, if alternatives are provided.

This parameter describes where *zugbruecke*'s parser can find a number (integer) which represents the length of the memory block or, alternatively, arguments for a custom length function.

It is expected to be either a single path list like ``[0, 'field_a']`` or a tuple of multiple (or even zero) path lists, if the optional ``f`` key (custom length function) is defined.

.. _nullstring:

Key: ``n``, NULL-terminated string flag
---------------------------------------

- Type: ``bool``
- Default: ``False``
- Optional

Can be set to ``True`` if a NULL-terminated string is passed as an argument. ``memsync`` will automatically determine the length of the string, so no extra information on its length is required. ``l`` can be omitted.

.. _unicodechar:

Key: ``w``, Unicode character flag
----------------------------------

- Type: ``bool``
- Default: ``False``
- Optional

If a Unicode string (buffer) is passed into a function, this parameter must be set to ``True``. Only relevant if ``n`` is also set to ``True``.

.. _pointertype:

Key: ``t``, data type of pointer
--------------------------------

- Type: ``str`` (name of a PyCSimpleType or PyCStructType type)
- Default: ``'c_ubyte'``
- Optional

This field expects a string representing the name of a *ctypes* datatype. If you want to specify a custom structure type, you simply specify its class name as a string instead. This parameter will be used by ``ctypes.sizeof`` for determining the datatype's size in bytes. The result is then multiplied with the ``length`` to get an actual size of the memory block in bytes.

For details on ``sizeof``, consult the `Python documentation on sizeof`_. It will accept `fundamental types`_ as well as `structure types`_.

.. _Python documentation on sizeof: https://docs.python.org/3/library/ctypes.html?highlight=ctypes#ctypes.sizeof
.. _fundamental types: https://docs.python.org/3/library/ctypes.html?highlight=ctypes#fundamental-data-types
.. _structure types: https://docs.python.org/3/library/ctypes.html?highlight=ctypes#ctypes.Structure

.. _length function:

Key: ``f``, custom function for computing the length of the memory segment
--------------------------------------------------------------------------

- Type: ``str`` (code of self-contained lambda or Python function)
- Optional

This field can be used to provide in a string, which can be parsed into a function or lambda expression for computing the ``length`` of the memory section from multiple parameters. If provided, the function receives the data gathered via the path(s) provided in ``l`` as arguments.

.. _customtype:

Key: ``_c``, custom data type
-----------------------------

- Type: ``type``
- Optional

If you are using a custom non-*ctypes* datatype, which offers a ``from_param`` method, you must specify it here. This applies if you are constructing your own array types or use *numpy* types for instance.
