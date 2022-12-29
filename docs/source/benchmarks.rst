:github_url:

.. _benchmarks:

.. index::
	single: speed
	single: benchmark
	single: optimization
	pair: overhead; call

Benchmarks
==========

*zugbruecke* performs reasonably well given its complexity with **0.15 ms overhead per simple function call** on average on modern hardware. Very complex function calls involving callback functions and memory synchronization can involve an overhead of several milliseconds.

.. note::

	*zugbruecke* is not yet optimized for speed. The inter-process communication via *multiprocessing connection* adds overhead to every function call. Because *zugbruecke* takes care of packing and unpacking of pointers and structures for arguments and return values, this adds another bit of overhead. Calls are slow in general, but the first call of an individual routine within a session is even slower due to necessary initialization happening beforehand. Depending on the use-case, instead of working with *zugbruecke*, it will be significantly faster to isolate functionality depending on DLL calls into a dedicated *Python* script and run it directly with a *Windows Python* interpreter under *Wine*. *zugbruecke* offers a :ref:`Wine Python Environment <wineenv>` for this purpose.

For comparison and overhead measurements, see the individual benchmarks.

.. include:: benchmarks_all.rst

.. include:: benchmarks_sysinfo.rst

*zugbruecke* was :ref:`configured <configuration>` with ``log_level`` set to ``0`` (logs off) for minimal overhead. For the corresponding source code, both Python and C, check the `benchmark directory`_ of this project.

.. _benchmark directory: https://github.com/pleiszenburg/zugbruecke/tree/master/benchmark
