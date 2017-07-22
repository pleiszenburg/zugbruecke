.. _interoperability:

.. index::
	single: motivation
	single: use cases

Introduction
============

.. _motivation:

Motivation
----------

Academic interest and frustration over the lack of a project of this kind, mostly.
*zugbruecke* ultimately started as an attempt to collect and consolidate a
sizable collection of "ugly hacks" accumulated over the years. Those had mostly been
written for accessing routines for complicated numerical computations in proprietary DLLs
on Linux clusters.

The need for calling individual routines offered by DLLs
from *Linux*/*MacOS*/*BSD* software/scripts is reflected in numerous threads in forums and
mailing lists reaching back well over a decade. The recommended approach so far
has been (and still is!) to write a *Wine* application, which links against ``winelib``,
thus allowing to access DLLs. Wine applications can also access libraries
on the *Unix* "host" system, which provides the desired bridge between both worlds.
Nevertheless, this approach is anything but trivial. *zugbruecke* is supposed
to satisfy the desire for a "quick and dirty" solution for calling routines from a
high level scripting language, *Python*, directly running on the *Unix* "host" system.
With respect to "quick", *zugbruecke* works just out of the box with *Wine* installed.
No headers, compilers, cross-compilers or any other configuration is required - one
import statement followed by well established ``ctypes`` syntax is enough.
It is pure *Python* doing its job.
With respect to "dirty", well, read the project's documentation from start to finish.

.. _implementation:

The magic behind the curtain - or how it is implemented
-------------------------------------------------------

During the first import of *zugbruecke*, a stand-alone *Windows*-version of the
*CPython* interpreter corresponding to the used *Unix*-version is automatically
downloaded and placed into the module's configuration folder (by default located at
``~/.zugbruecke/``). Next to it, also during first import, zugbruecke
generates its own *Wine*-profile directory for being used with a dedicated
``WINEPREFIX``. This way, any undesirable interferences with other *Wine*-profile
directories containing user settings and unrelated software are avoided.

During every import, *zugbruecke* starts the *Windows* *Python* interpreter on top of *Wine*.
It is used to run a server script named ``_server_.py``, located in the module's folder.

*zugbruecke* offers everything *ctypes* would on the *Unix* system it is running on
plus everything *ctypes* would offer if it was imported under *Windows*. Functions
and classes, which have a platform-specific behavior, are replaced with dispatchers.
The dispatchers decide whether the *Unix* or the *Windows* behavior should be used
depending on the context of how they were invoked and what parameters were passed
into them. If *Windows* specific behavior is chosen, calls are passed from
*zugbruecke*'s client code running on *Unix* to the server component of *zugbruecke*
running on *Wine*.

.. _usecases:

Use cases - or when you should consider using this project
----------------------------------------------------------

- Quickly calling routines in proprietary DLLs.

- Reading legacy file formats and running mission critical legacy plugins
  for legacy ERP software in a modern environment comes to mind.

- Calling routines in DLLs which come, for some odd reason like "developer suddenly
  disappeared with source code", without source code.
  DLLs found in company-internal software or R&D projects come to mind.

- More common than one might think, calling routines in DLLs, of which the source code is available but
  can not be (re-)compiled (on another platform) / understood / ported for similarly
  odd reasons like "developer retired and nobody knows how to do this" or "developer 'went on'
  and nobody manages to understand the undocumented code". The latter is especially
  prevalent in academic environments, where what is left of years of hard work might
  only be a single "binary blob" - a copy of an old DLL file. All sorts of complicated
  and highly specialized numerical computations come to mind.
