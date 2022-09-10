:github_url:

.. _benchmarks:

.. index::
	single: speed
	single: benchmark
	single: optimization
	pair: overhead; call

Benchmarks
==========

*zugbruecke* performs reasonably well given its complexity with **less than 0.2 µs overhead per call** in average on modern hardware.

.. note::

	*zugbruecke* is not yet optimized for speed.

The inter-process communication via *multiprocessing connection* adds overhead to every function call. Because *zugbruecke* takes care of packing and unpacking of pointers and structures for arguments and return values, this adds another bit of overhead. Calls are slow in general, but the first call of an individual routine within a session is even slower due to necessary initialization happening beforehand. Depending on the use-case, instead of working with *zugbruecke*, it will be significantly faster to isolate functionality depending on DLL calls into a dedicated *Python* script and run it directly with a *Windows Python* interpreter under *Wine*. *zugbruecke* offers a :ref:`Wine Python Environment <wineenv>` for this purpose.

For comparison and overhead measurements, see the following numbers:

===================  ==============  ================== ================= ================== ============================
example call         iterations [#]  w/o zugbruecke [s] w/ zugbruecke [s] overhead/call [ns] parameter features
===================  ==============  ================== ================= ================== ============================
simple_demo_routine  100k            0.101              11.273            111.7              2x by value
gdc                  100k            0.104              11.318            112.1              2x by value
in_mandel (inside)   100k            0.518              11.719            112.0              3x by value
in_mandel (outside)  100k            0.131              11.494            113.6              3x by value
divide               100k            0.174              11.808            116.3              2x by value, 1x by reference
distance             100k            0.230              12.760            125.3              2x struct by reference
===================  ==============  ================== ================= ================== ============================

Benchmarks were performed with an *i7* 3740QM CPU, *Linux* kernel 4.4.72, *Wine* 2.10, *CPython* 3.6.1 x86-64 for *Linux* and *CPython* 3.5.3 x86-32 for *Windows*. *zugbruecke* was :ref:`configured <configuration>` with ``log_level`` set to ``0`` (logs off) for minimal overhead.

For the corresponding DLL source code (written in C) check the `demo_dll directory`_ of this project. For the corresponding Python code check the `examples directory`_ of this project.

.. _examples directory: https://github.com/pleiszenburg/zugbruecke/tree/master/examples
.. _demo_dll directory: https://github.com/pleiszenburg/zugbruecke/tree/master/examples/demo_dll
