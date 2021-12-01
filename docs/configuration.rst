:github_url:

.. _configuration:

.. index::
    pair: python; version
    triple: python; arch; architecture
    triple: wine; arch; architecture
    triple: log; level; write
    statement: zugbruecke.ctypes.zb_set_parameter
    module: zugbruecke.Config

Configuration
=============

*zugbruecke* can automatically configure itself or can be configured manually. The configuration allows you to fine-tune its verbosity, architecture and other relevant parameters on a per-session basis. By importing ``zugbruecke.ctypes``, a default session is started and configured automatically. Alternatively, you can create and configure your own sessions manually by creating instances of :class:`zugbruecke.CtypesSession`. See the :ref:`chapter on the session model <session>` for details. Sessions can be configured :ref:`at the time of their creation <configconstructor>` as well as :ref:`at run-time <reconfiguration>`.

.. toctree::
   :maxdepth: 2
   :caption: Configuration in Detail

   configparameters
   configclass
