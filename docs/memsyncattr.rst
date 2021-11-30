The ``memsync`` attribute
=========================

``memsync`` is a list of dictionaries. Every dictionary represents one memory
section, which must be kept in sync. It has the following keys:

* ``p`` (:ref:`path to pointer <pathpointer>`)
* ``l`` (:ref:`path to length <pathlength>`, optional)
* ``n`` (:ref:`NULL-terminated string flag <nullstring>`, optional)
* ``w`` (:ref:`Unicode character flag <unicodechar>`, optional)
* ``t`` (:ref:`data type of pointer <pointertype>`, optional)
* ``f`` (:ref:`custom length function <length function>`, optional)
* ``_c`` (:ref:`custom data type <customtype>`, optional)

.. _pathpointer:

Key: ``p``, path to pointer (list of int and/or str)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This parameter describes where in the arguments or return value
(along the lines of ``argtypes`` and ``restype``)
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

Return values or elements within can be targeted by setting the first element
of a path to ``'r'`` (instead of an integer targeting an argument).

.. _pathlength:

Key: ``l``, path to length (list of int and/or str OR tuple of lists of int and/or str) (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This parameter works just like the :ref:`path to pointer <pathpointer>` parameter.
It is expected to tell the parser, where it can find a number (int) which represents
the length of the memory block or, alternatively, arguments for a custom length function.

It is expected to be either a single path list like ``[0, 'field_a']`` or a tuple
of multiple (or even zero) path lists, if the optional ``f`` key (custom length function) is defined.

.. _nullstring:

Key: ``n``, NULL-terminated string flag (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Can be set to ``True`` if a NULL-terminated string is passed as an argument.
``memsync`` will automatically determine the length of the string, so no
extra information on its length (through ``l`` is required).

.. _unicodechar:

Key: ``w``, Unicode character flag (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a Unicode string (buffer) is passed into a function, this parameter must be
set to ``True``. If not specified, it will default to ``False``.

.. _pointertype:

Key: ``t``, data type of pointer (PyCSimpleType or PyCStructType) (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This field expects a string representing the name of a ctypes datatype.
If you want to specify a custom structure type, you simply specify its class name as a string instead.

This parameter will be used by ``ctypes.sizeof`` for determining the datatype's size in bytes.
The result is then multiplied with the ``length`` to get an actual size of the
memory block in bytes. If it is not explicitly defined, it defaults to ``'c_ubyte'``.

For details on ``sizeof``, consult the `Python documentation on sizeof`_.
It will accept `fundamental types`_ as well as `structure types`_.

.. _Python documentation on sizeof: https://docs.python.org/3/library/ctypes.html?highlight=ctypes#ctypes.sizeof
.. _fundamental types: https://docs.python.org/3/library/ctypes.html?highlight=ctypes#fundamental-data-types
.. _structure types: https://docs.python.org/3/library/ctypes.html?highlight=ctypes#ctypes.Structure

.. _length function:

Key: ``f``, custom function for computing the length of the memory segment (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This field can be used to plug in a string, which can be parsed into a function or
lambda expression for computing the ``length`` of the memory section from multiple parameters.
The function is expected to accept a number of arguments equal to the number of elements
of the tuple of length paths defined in ``l``.

.. _customtype:

Key: ``_c``, custom data type (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are using a custom non-*ctypes* datatype, which offers a ``from_param`` method,
you must specify it here. This applies when you construct your own array types
or use *numpy* types for instance.
