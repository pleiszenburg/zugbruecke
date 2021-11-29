:github_url:

.. _session:

.. index::
	single: zugbruecke.ctypes
	single: zugbruecke.CtypesSession

Session Model
=============

*zugbruecke* operates based on a session model. Each session represents a separate *Windows* *Python* interpreter process running on top of *Wine*. *zugbruecke* starts a default session during the import of ``zugbruecke.ctypes``, but the user can start more and distinctly configured sessions if required manually by creating instances of :class:`zugbruecke.CtypesSession`.

.. toctree::
   :maxdepth: 2
   :caption: The Session Model in Detail

   sessionoverview
   sessionclass
