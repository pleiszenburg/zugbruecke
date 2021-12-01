:github_url:

.. _memsync:

.. index::
	single: pointer

Handling Pointers
=================

Because *zugbruecke* runs code in a separate *Windows Python* interpreter on *Wine*, pointers pose a special kind of problem. They can, unfortunately, not be passed from the code running on the *Unix* side to the code running on the *Wine* side or vice versa. This is why the memory (to where pointers are pointing) must be kept in sync on both sides. Memory synchronization can be controlled by the user through the ``memsync`` protocol. ``memsync`` implements special directives, which do not interfere with *ctypes* should the code be required to run on *Windows* as well.

*zugbruecke* can handle some types of pointers on its own, without additional ``memsync`` directives. Pointers to variables containing a single element - e.g. a floating pointer number or a structure - and pointers to fixed-length arrays are handled transparently without additional directives. If, on the other hand, the size of the memory a pointer is pointing to is dynamically determined at runtime, *zugbruecke* must be provided with a hint on where it can find information on the size of the memory section within the arguments or return value of a routine call. Those hints can be provided through ``memsync``.

.. toctree::
   :maxdepth: 2
   :caption: Memory Synchronization in Detail

   memsyncprotocol
   memsyncattr
