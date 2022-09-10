.. _memsyncprotocol:

The Memory Synchronization Protocol
===================================

A Simple Example
----------------

This first example walks through how to handle an array of floating point numbers of arbitrary length. Consider the following example routine written in C and compiled into a DLL:

.. code:: C

    void
    __stdcall __declspec(dllimport)
    bubblesort(
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

It is a simple implementation of the "bubblesort" algorithm, which accepts a pointer to an array of floats of arbitrary length and an integer with length information. The array is being sorted within its own memory, so the caller expects a sorted array at the passed pointer after the call.

With *ctypes* on *Windows*, you could call the function as follows:

.. code:: python

    from ctypes import windll, cast, pointer, POINTER, c_float, c_int
    from typing import List

    _dll = windll.LoadLibrary('demo.dll')
    _bubblesort = _dll.bubblesort
    _bubblesort.argtypes = (POINTER(c_float), c_int)

    def bubblesort(values: List[float]):

        float_array = ((c_float)*len(values))(*values)
        pointer_firstelement = cast(pointer(float_array), POINTER(c_float))
        _bubblesort(pointer_firstelement, len(values)) # call into DLL
        values[:] = float_array[:]

    test_vector = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
    bubblesort(test_vector)

For running the same code with *zugbruecke* on *Unix*, you need to add information on the memory segment representing the array. This is done by adding another attribute, ``memsync``, to the ``_bubblesort`` function handle (just like you usually specify ``argtypes`` and/or ``restype``). The following example demonstrates how the above example must be modified for it to work with *zugbruecke*:

.. code:: python

    from typing import List
    from zugbruecke.ctypes import windll, cast, pointer, POINTER, c_float, c_int

    _dll = windll.LoadLibrary('demo.dll')
    _bubblesort = _dll.bubblesort
    _bubblesort.argtypes = (POINTER(c_float), c_int)
    _bubblesort.memsync = [
        {
            'p': [0], # pointer argument
            'l': [1], # length argument
            't': 'c_float', # array element type
        }
    ]

    def bubblesort(values: List[float]):

        float_array = ((c_float)*len(values))(*values)
        pointer_firstelement = cast(pointer(float_array), POINTER(c_float))
        _bubblesort(pointer_firstelement, len(values)) # call into DLL
        values[:] = float_array[:]

    test_vector = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
    bubblesort(test_vector)

Two things have changed. First, the import statement turned from *ctypes* to *zugbruecke*, although the exact same types, routines and objects were imported. Second, the ``_bubblesort`` function handle received an additional ``memsync`` attribute.

.. note::

    Because the ``memsync`` attribute will be ignored by *ctypes*, you can make the above piece of code platform-independent by adjusting the import statement only.

The complete example, which will run on *Unix* and on *Windows* looks just like this:

.. code:: python

    from sys import platform
    if any(platform.startswith(os_name) for os_name in ('linux', 'darwin', 'freebsd')):
        from zugbruecke.ctypes import windll, cast, pointer, POINTER, c_float, c_int # Unix
    elif platform.startswith('win'):
        from ctypes import windll, cast, pointer, POINTER, c_float, c_int # Windows
    else:
        raise SystemError('unsupported platform')

    _dll = windll.LoadLibrary('demo.dll')
    _bubblesort = _dll.bubblesort
    _bubblesort.argtypes = (POINTER(c_float), c_int)
    _bubblesort.memsync = [
        {
            'p': [0], # pointer argument
            'l': [1], # length argument
            't': 'c_float', # array element type
        }
    ]

    def bubblesort(values: List[float]):

        float_array = ((c_float)*len(values))(*values)
        pointer_firstelement = cast(pointer(float_array), POINTER(c_float))
        _bubblesort(pointer_firstelement, len(values)) # call into DLL
        values[:] = float_array[:]

    test_vector = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
    bubblesort(test_vector)

A Complex Example
-----------------

This second example walks through how to compute the size of the memory from multiple arguments. There are plenty of cases where you will encounter function (or structure) definitions as follows:

.. code:: C

    void
    __stdcall __declspec(dllimport)
    process_image(
        float *image_data,
        int image_width,
        int image_height
    );

The ``image_data`` parameter is a flattened 1D array representing a 2D image. Its length is defined as the product of its width and its height. So the length of the array equals ``image_width * image_height``. For cases like this, ``memsync`` has the ability to dynamically compute the length of the memory through custom functions. Let's have a look at how the above function would be configured in *Python*:

.. code:: python

    process_image.argtypes = (ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_int)
    process_image.memsync = [
        {
            'p': [0], # pointer argument
            'l': ([1], [2]), # length arguments
            'f': 'lambda x, y: x * y', # function for computing length
            't': 'c_float', # array element type
        }
    ]

The above definition will extract the values of the ``image_width`` and ``image_height`` parameters for every function call and feed them into the specified lambda function.

String Buffers, Null-Terminated Strings and Unicode
---------------------------------------------------

Let's assume you are confronted with a regular *Python* (3) string. With the help of a DLL function, you want to replace all occurrences of a letter with another letter.

.. code:: python

    some_string = 'zategahuba'

The DLL function is defined as follows:

.. code:: C

    void
    __stdcall __declspec(dllimport)
    replace_letter(
        char *in_string,
        char old_letter,
        char new_letter
    );

In *Python*, it can be configured as follows:

.. code:: python

    replace_letter.argtypes = (
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_char,
        ctypes.c_char,
        )
    replace_letter.memsync = [
        {
            'p': [0], # pointer argument
            'n': True, # null-terminated string flag
        }
    ]

The above configuration indicates that the first argument of the function is a pointer to a NULL-terminated string.

While *Python* (3) strings are actually Unicode strings, the function accepts an array of type ``char`` - a bytes array in *Python* terms. I.e. you have to encode the string before it is copied into a string buffer. The following example illustrates how the function ``replace_letter`` can be called on the string ``some_string``, exchanging all letters ``a`` with ``e``. Subsequently, the result is printed.

.. code:: python

    string_buffer = ctypes.create_string_buffer(some_string.encode('utf-8'))
    replace_letter(string_buffer, 'a'.encode('utf-8'), 'e'.encode('utf-8'))
    print(string_buffer.value.decode('utf-8'))

The process differs if the DLL function accepts Unicode strings. Let's assume the DLL function is defined as follows:

.. code:: C

    void __stdcall __declspec(dllimport) replace_letter_w(
        wchar_t *in_string,
        wchar_t old_letter,
        wchar_t new_letter
        );

In Python, it can be configured like this:

.. code:: python

    replace_letter_w.argtypes = (
        ctypes.POINTER(ctypes.c_wchar),
        ctypes.c_wchar,
        ctypes.c_wchar,
        )
    replace_letter_w.memsync = [
        {
            'p': [0], # pointer argument
            'n': True, # null-terminated string flag
            'w': True, # Unicode flag
        }
    ]

One key aspect has changed: ``memsync`` contains another field, ``w``. It must be set to ``True``, indicating that the argument is a Unicode string. Now you can call the function as follows:

.. code:: python

    unicode_buffer = ctypes.create_unicode_buffer(some_string)
    replace_letter_w(unicode_buffer, 'a', 'e')
    print(unicode_buffer.value)

Callbacks / Function Pointers
-----------------------------

.. note::

    Function pointers themselves do not require memory synchronization.

Arguments and/or return values of function pointers might require memory synchronization just like the arguments and return values of other functions. Let's assume that you are dealing with structures of the following kind:

.. code:: python

    class image_data(ctypes.Structure):
        _fields_ = [
            ('data', ctypes.POINTER(ctypes.c_int16)),
            ('width', ctypes.c_int16),
            ('height', ctypes.c_int16),
        ]

2D monochrome image data is represented as a flattened 1D array, field ``data``, with size information attached to it in the fields ``width`` and ``height``. You furthermore have a function prototype which accepts an ``image_data`` structure as an argument:

.. code:: python

    filter_func_type = ctypes.WINFUNCTYPE(ctypes.c_int16, ctypes.POINTER(image_data))

Before you actually decorate a *Python* function with it, all you have to do is to change the contents of the ``memsync`` attribute of the function prototype, ``filter_func_type``:

.. code:: python

    filter_func_type.memsync = [
        {
            'p': [0, 'data'], # pointer argument
            'l': ([0, 'width'], [0, 'height']), # length arguments
            'f': 'lambda x, y: x * y', # function for computing length
            't': 'c_int16', # array element type
        }
    ]

.. note::

	The above syntax also does not interfere with ``ctypes`` on *Windows*, i.e. the code remains perfectly platform-independent.

Once the function prototype has been configured through ``memsync``, it can be applied to a *Python* function:

.. code:: python

    @filter_func_type
    def filter_edge_detection(in_buffer):
        # do something ...
