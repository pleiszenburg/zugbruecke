.. _session:

.. index::
	single: session
	single: current_session

The session model
=================

*zugbruecke* operates based on a session model. Every session represents
a separate *Windows* *Python* interpreter process running on *Wine*. By default,
*zugbruecke* starts one session during import, but the user can start more
sessions if required. Sessions are identified by a unique (hash) ID string.

.. _sessionclass:

Class: ``zugbruecke.session``
-----------------------------

By creating an instance of this class, a new session can be started. The number
of instances is only (theoretically) limited by the amount of available memory
and by the number of available network ports on the host system (two ports per
instance are required). The :ref:`constructor can be configured <configconstructor>`.

.. _currentsessionobject:

Instance: ``zugbruecke.current_session``
----------------------------------------

x
