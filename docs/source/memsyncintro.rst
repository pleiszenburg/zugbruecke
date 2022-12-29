:github_url:

.. _memsyncintro:

Introduction to Memory Synchronization
======================================

Because *zugbruecke* runs code in a separate *Windows Python* interpreter on *Wine*, pointers pose a special kind of problem. They can, unfortunately, not be passed from the code running on the *Unix* side to the code running on the *Wine* side or vice versa "as is" thanks to `memory protection`_. This is why pointers must be translated and data in memory kept in sync on both sides. In many cases, *zugbruecke* can do this fully automatically. There are cases however where memory synchronization must be controlled by the user through the ``memsync`` protocol.

.. note::

    ``memsync`` implements special directives, which extend regular *ctypes* syntax but do not interfere with *ctypes* should the code be required to run on *Windows* as well.

Where is memory synchronized automatically?
-------------------------------------------

*zugbruecke* can handle some types of pointers on its own, without additional ``memsync`` directives. Pointers to variables containing a single element - e.g. a floating point number or a structure - and pointers to fixed-length arrays are handled transparently without additional directives.

In more technical terms, whenever ``ctypes.sizeof(your_argument_type)`` would give a meaningful result right out of the gate, i.e. the size of the memory to be synchronized can be determined from data types provided via ``argtypes`` and/or ``restype``, ``memsync`` is not required. This also applies to more complex types such as structures where ``ctypes.POINTER(your_struct_type)`` is just fine on its own as long as only a single structure is passed back and forth.

Arrays can be handled automatically as well if they have a fixed, specified length. Type definitions given via ``argtypes`` and/or ``restype`` such as ``ctypes.POINTER(ctypes.c_int * 10)`` or even ``ctypes.POINTER(your_struct_type * 10)`` are fine because their size can clearly be deduced from the type itself.

Last but not least, every bit of data that is passed truly "by value" instead of as a pointer does not require ``memsync``.

.. warning::

    Data passed "by value" can be confusing because original *ctypes* does accept data passed "by value" in certain cases but actually passes a pointer into the DLL function internally. Zero/null-terminated string buffers are a good example for this problem. Here, *zugbruecke* is a bit more strict: It forces the user to specify pointer types in ``argtypes`` where applicable. Passing data "implicitly by reference" is not supported by *zugbruecke* in most scenarios. Such cases can require ``memsync`` as a consequence. Implicitly passing data by reference only really works with *zugbruecke* for "simply data types", i.e. individual integers and floating point numbers.

Where is ``memsync`` required?
------------------------------

If the size of a chunk of memory a pointer is pointing to is arbitrary and dynamically determined at runtime, i.e. once per function call, *zugbruecke* must be provided with a hint on where it can find information on the size of the memory section within the arguments or return value of a routine call. Arrays of arbitrary length are classic examples. Besides, if null/zero-terminated string buffers are passed via ``ctypes.POINTER(ctypes.c_char)`` or similar, *zugbruecke** must be made aware of this fact. Those hints can be provided through ``memsync``.

.. _memory protection: https://en.wikipedia.org/wiki/Memory_protection
