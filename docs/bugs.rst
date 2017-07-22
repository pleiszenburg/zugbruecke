.. _bugs:

Bugs
====

Please report bugs in *zugbruecke* in *zugbruecke*'s `GitHub issue tracker`_.

Please report bugs *ctypes* in the 'Python tracker'_.

Please report bugs in *Wine* in the `WineHQ Bug Tracking System`_.

Make sure to separate between *zugbruecke*-related, *ctypes*-related and
*Wine*-related bugs.

.. _GitHub issue tracker: https://github.com/pleiszenburg/zugbruecke/issues
.. _Python tracker: https://bugs.python.org/
.. _WineHQ Bug Tracking System: https://bugs.winehq.org/

How to bisect issues
--------------------

*zugbruecke* is based on a session model. Each session can be launched with
parameters, which can either be passed into or picked up from a configuration file
by the session constructor. It is also possible to change parameters during run-time.

If you want to increase the log level during run-time, you can do the following:

.. code:: python

	import zugbruecke
	# work with zugbruecke
	zugbruecke.current_session.set_parameter({'log_level': 10})
	# proceed as usual - with a lot more verbosity

Alternatively, you can drop a configuration file named ``.zugbruecke.json`` into
your current working directory or *zugbruecke*'s configuration directory (likely
``~/.zugbruecke``) and add configuration parameters to it like
``{"log_level": 10, "logwrite": true}``.

The higher the log level, the more output you will get. Default is 0 for no logs.
The on-screen log is color-coded for readability. The log can also, in addition,
be written to disk, where every log item with plenty of meta data is represented
as a one-line JSON object for easy parsing and analysis of larger log files.

For more configuration objects check the :ref:`chapter on configuration <configuration>`.

As an alternative approach, you can also check what happens if you
run your code directly in a *Windows* *Python* interpreter with *ctypes*.
Consult the :ref:`chapter on the Wine Python environment <wineenv>`
for details. It is easy to get *ctypes* syntax wrong, so this is a good
approach for getting it right. 

If in doubt, please also test your code with *ctypes* on an actual Windows
system - it might be a bug in this module as well.
