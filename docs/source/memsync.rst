:github_url:

.. _memsync:

.. index::
	single: pointer

Pointers & Memory Synchronization
=================================

*zugbruecke* needs to translate pointers and synchronize memory between two processes. This section explains how this is done and when special ``memsync`` directives, extending regular *ctypes* syntax, are required.

.. toctree::
   :maxdepth: 2
   :caption: Memory Synchronization in Detail

   memsyncintro
   memsyncprotocol
   memsyncattr
