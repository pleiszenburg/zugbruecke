.. _bugs:

Bugs
====

Please report bugs in zugbruecke in the zugbruecke GitHub repository: https://github.com/pleiszenburg/zugbruecke/issues

Please report bugs in Wine in the WineHQ Bug Tracking System: https://bugs.winehq.org/

Make sure to separate between zugbruecke-related and Wine-related bugs.
Calling routines in DLLs from Windows-executables (executed with Wine) with identical
parameters for narrowing down the possible sources of an error is a good way to start.

How to bisect issues
--------------------

zugbruecke is based on a session model. Each session can be launched with
parameters, which can either be passed into or picked up from a configuration file
by the session constructor. It is also possible to change parameters during run-time.

If you want to increase the log level during run-time, you can do the following:

.. code:: python

	import zugbruecke
	# work with zugbruecke
	zugbruecke.current_session.set_parameter({'log_level': 10})
	# proceed as usual - with a lot more verbosity

Alternatively, you can drop a configuration file named ``.zugbruecke.json`` into
your current working directory or zugbruecke's configuration directory (likely
``~/.zugbruecke``) and add configuration parameters to it like
``{"log_level": 10, "logwrite": true}``.

The higher the log level, the more output you will get. Default is 0 for no logs.
The on-screen log is color-coded for readability. The log can also, in addition,
be written to disk, where every log item with plenty of meta data is represented
as a one-line JSON object for easy parsing and analysis of larger log files.

Have a look into the routine ``get_default_config`` in ``src/zugbruecke/config.py`` for
a comprehensive overview over all possible parameters.
