:github_url:

.. _introduction:

.. index::
	single: motivation
	single: implementation
	single: use cases

About ``zugbruecke``
====================

.. _synopsis:

Synopsis
--------

*zugbruecke* is an **EXPERIMENTAL** *Python* module (currently in development *status 3/alpha*). It allows to call routines in *Windows* DLLs from *Python* code running on Unices / *Unix*-like systems such as *Linux*, *MacOS* or *BSD*. *zugbruecke* is designed as a drop-in replacement for *Python*'s standard library's *ctypes* module. *zugbruecke* is built on top of `Wine`_. A stand-alone *Windows* *Python* interpreter launched in the background is used to execute the called DLL routines. Communication between the *Unix*-side and the *Windows*/*Wine*-side is based on *Python*'s
build-in multiprocessing connection capability. *zugbruecke* has (limited) support for pointers, struct types and call-back functions. *zugbruecke* comes with extensive logging features allowing to debug problems associated with both itself and with *Wine*. *zugbruecke* is written using *Python* 3 syntax and primarily targets the *CPython* implementation of *Python*.

.. _Wine: https://www.winehq.org/

.. _motivation:

Motivation & Alternatives
-------------------------

Academic interest and frustration over the lack of a project of this kind, mostly. *zugbruecke* ultimately started as an attempt to collect and consolidate a sizable collection of "ugly hacks" accumulated over the years. Those had mostly been written for accessing routines for complicated numerical computations in proprietary DLLs on Linux clusters.

The need for calling individual routines offered by DLLs from *Linux*/*MacOS*/*BSD* software/scripts is reflected in numerous threads in forums and
mailing lists reaching back well over two decades. The recommended approach so far has been (and still is!) to write a *Wine* application, which links against ``winelib``, thus allowing to access DLLs. Wine applications can also access libraries on the *Unix* "host" system, which provides the desired bridge between both worlds. Nevertheless, this approach is anything but trivial.

Alternative solutions with a somewhat more narrow scope were motivated by the desire to make proprietary Windows modem and WIFI drivers work on Linux. Examples include the proprietary, now discontinued `DriverLoader`_ by `Linuxant`_ as well as the still maintained open source `ndiswrapper project`_. Both projects are providing thin wrappers for allowing to load and run Windows DLLs while offering only actually required Windows system APIs to them. Based upon this concept, security researcher `Tavis Ormandy`_ built the `loadlibrary project`_ for scalable and efficient fuzzing of self-contained Windows libraries on Linux, primarily targeting Windows Defender. Although ``loadlibrary`` can, strictly speaking, run any type of DLL, one must implement every call into Windows APIs manually - a task that can quickly become as complicated as developing something like *Wine* from scratch.

.. _DriverLoader: http://www.linuxant.com/driverloader/
.. _Linuxant: http://www.linuxant.com
.. _ndiswrapper project: https://sourceforge.net/projects/ndiswrapper/
.. _Tavis Ormandy: https://github.com/taviso
.. _loadlibrary project: https://github.com/taviso/loadlibrary

*zugbruecke* is supposed to satisfy the desire for a "quick and dirty" solution for calling routines from a high level scripting language, *Python*, directly running on the *Unix* "host" system. With respect to "quick", *zugbruecke* works just out of the box with *Wine* installed. No headers, compilers, cross-compilers or any other configuration is required - one ``import`` statement followed by well established ``ctypes`` syntax is enough. It is pure *Python* doing its job. With respect to "dirty", well, read the project's documentation from start to finish.

.. _implementation:

Implementation
--------------

During the first import of ``zugbruecke.ctypes``, a stand-alone *Windows*-version of the *CPython* interpreter is automatically downloaded and placed into the current virtual environment's ``share`` folder (by default located at ``{sys.prefix}/shared/wenv/``). Next to it, also during first import, *zugbruecke* generates its own *Wine*-profile directory for being used with a dedicated ``WINEPREFIX``. This way, any undesirable interference with other *Wine*-profile directories containing user settings and unrelated software are avoided. The management of this :ref:`Wine Python environment <wineenv>` is handled by a `dedicated Python package named wenv`_.

.. _dedicated Python package named wenv: https://wenv.readthedocs.io/en/latest/

During every import of ``zugbruecke.ctypes``, *zugbruecke* starts the *Windows* *Python* interpreter on top of *Wine*. It is used to run a server script named ``_server_.py``, located in the module's folder. If multiple *Windows* *Python* interpreter processes are required, for instance for calling into both 32 bit and 64 bit DLLs, *zugbruecke* also allows to start and manage multiple :ref:`ctypes sessions <session>` via the :class:`zugbruecke.CtypesSession` class. Importing ``zugbruecke.ctypes`` is therefore merely a shortcut to creating a single instance of this class with default settings. :class:`zugbruecke.CtypesSession` objects offer everything *ctypes* offer if it was imported under *Windows*.

.. _usecases:

Use Cases
---------

- Quickly calling routines in proprietary DLLs.
- Reading legacy file formats and running mission critical legacy plugins for legacy ERP software in a modern environment comes to mind.
- Driving aged laboratory equipment via old Windows drivers from modern Linux machines.
- Calling routines in DLLs which come, for some odd reason like "developer suddenly disappeared with source code", without source code. DLLs found in company-internal software and R&D projects come to mind.
- More common than one might think, calling routines in DLLs, of which the source code is available but can not be (re-)compiled (on another platform) or understood or ported for similarly odd reasons like "developer retired and nobody knows how to do this" or "developer 'went on' and nobody manages to understand the undocumented code". The latter is especially prevalent in academic environments, where what is left of years or even decades of hard work might only be a single "binary blob" - a copy of an old DLL file. All sorts of complicated and highly specialized numerical computations come to mind.
