:github_url:

.. _wineenv:

.. index::
	single: wenv python
	single: wenv pip
	single: wenv pytest
	single: wenv init
	triple: wine; python; environment
	module: zugbruecke.wenv

Wine Python environment
=======================

*zugbruecke* offers a useful helper script named ``wenv`` which allows to work with *Python* on *Wine* more easily. It is also used for *zugbruecke*'s internal operations and development tests.

Command: ``wenv init``
----------------------

If you have not already used ``zugbruecke`` for calling into functions, you may have to initialize the *Wine Python environment* first by running ``wenv init``. This will configure *Wine*, install a *Windows* version of *Python* and fetch *pip*, *setuptools*, *pytest*, *coverage* and further dependencies.

Command: ``wenv clean``
-----------------------

This command is useful if you want to remove your current *Wine Python environment* and all related data (including the relevant *Wine* prefix). ``zugbruecke``'s configuration is left untouched.

Command: ``wenv help``
----------------------

This command provides help and lists all currently available sub-commands (such as ``init`` or ``python``).

Command: ``wenv python``
------------------------

This command behaves just like the regular ``python`` command in a *Unix* shell, except that it fires up a *Windows* *Python* interpreter on top of *Wine*. It works with all regular parameters and switches, accepts pipes and can be launched in interactive mode.

You can also use it for creating executable *Python* scripts by adding the following at their top: ``#!/usr/bin/env _wenv_python``. Do not forget ``chmod +x your_script.py``. Notice that there is a difference between the more general ``wenv python`` command and its alias ``_wenv_python``, which is meant to be used only with a shebang.

Command: ``wenv pip``
---------------------

This command behaves just like the regular ``pip`` command on *Unix*, except that it attempts to install *Python* packages into a dedicated *Python* environment under *Wine*. So if you need any specific packages in ``wenv python``, this is how you install them. Most packages written in pure *Python* should work just fine. Anything requiring a compiler during installation does not work. Packages / wheels with pre-compiled binary components in them might work, although this is largely untested territory. Feel free to report any (positive or negative) results.

Command: ``wenv pytest``
------------------------

This command behaves just like the regular ``pytest`` or ``py.test`` command on *Unix*. It is used for verifying how *ctypes* behaves on *Windows* / *Wine*. Every test *zugbruecke* passes when tested with ``pytest`` is also supposed to be passed by *ctypes* when tested with ``wenv pytest``.

Command: ``wenv init_coverage``
-------------------------------

This command enables coverage analysis across the entire *Wine Python environment*.
