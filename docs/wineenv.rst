.. _wineenv:

.. index::
	single: wine-python
	single: wine-pip
	single: wine-pytest
	triple: wine; python; environment
	module: zugbruecke.core.wineenv

Wine Python environment
=======================

*zugbruecke* offers a few useful helper scripts for allowing to work with
*Python* on *Wine* more easily. They are also used for *zugbruecke*'s internal
operations and development tests.

Command: ``wine-python``
------------------------

This command behaves just like the regular ``python`` command in a *Unix* shell,
except that it fires up a *Windows* *Python* interpreter on top of *Wine*. It works
will all regular parameters and switches, even excepts pipes and can be launched in
interactive mode.

You can also use it for creating executable *Python* scripts by adding the following
at their top: ``#!/usr/bin/env wine-python``. Do not forget ``chmod +x your_script.py``.

Command: ``wine-pip``
---------------------

This command behaves just like the regular ``pip`` command on *Unix*, except
that it attempts to install *Python* packages into a dedicated *Python* environment
under *Wine*. So if you need any specific packages in ``wine-python``, this is
how you install them. Most packages written in pure *Python* should work just fine.
Anything requiring a compiler during installation does not work.
Packages / wheels with pre-compiled binary components in them might work,
although this is largely untested territory. Feel free to report any
(positive or negative) results.

Command: ``wine-pytest``
------------------------

This command behaves just like the regular ``pytest`` or ``py.test`` command
on *Unix*. It is used for verifying how *ctypes* behaves on *Windows* / *Wine*.
Every test *zugbruecke* passes when tested with ``pytest`` is also supposed
to be passed by *ctypes* when tested with ``wine-pytest``.
