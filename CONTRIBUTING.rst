How to contribute to *zugbruecke*
=================================

Thank you for considering contributing to *zugbruecke*!
**Contributions are highly welcomed!**

Reporting issues
----------------

Issues are tracked on `Gitbub`_.

- Read the section on `bugs`_ in *zugbruecke*'s documentation.
- Describe what you expected to happen.
- If possible, include a `minimal, complete, and verifiable example`_ to help
  identify the issue. This also helps check that the issue is not with your
  own code.
- Describe what actually happened. Include the full traceback if there was an
  exception.
- Enable logging at the highest level (10) and add the log if possible.
- If logging does not seem to work, let *zugbruecke* write its logs into files.
- List your operating system, *Python*, *Wine* and *zugbruecke* versions. If
  possible, check if this issue is already fixed in the repository
  (development branch).

.. _bugs: docs/bugs.rst
.. _Gitbub: https://github.com/pleiszenburg/zugbruecke/issues
.. _minimal, complete, and verifiable example: https://stackoverflow.com/help/mcve

Project philosophy
------------------

A few rules, describing how this project is being developed:

- *zugbruecke* is a drop-in replacement for *ctypes*.
- Whatever works with *ctypes* under *Windows* / *Wine* is supposed to work with
  *zugbruecke* under *Unix*.
- Whatever works with *ctypes* under *Unix* is supposed to work with *zugbruecke*
  under *Unix* as well without limitations.
- Keep interferences with users' code at a minimum. I.e. do not make
  users write plenty of if-statements for handling platform-specific behavior.
  The ``memsync`` protocol, which is just ignored by *ctypes* on *Windows* / *Wine*,
  is a good example of how to implement no-interfering platform-specific
  behavior.
- *zugbruecke* is supposed to throw the exact same errors *ctypes* does.
- Tests have to work equally with *ctypes* under Wine and with *zugbruecke* under *Unix*.
  Have a look at the implementation of ``make test`` for clarification.
- If something does not work with *ctypes* under *Windows* / *Wine*, *zugbruecke* is not expected
  to do it either. In this case, submit a patch to 'upstream' *CPython* instead first.
  Exceptions can be made if extra features are required for platform interoperability,
  like for instance converting paths from Unix to Windows format or vice versa.
- Code maintainability comes first (until further notice), speed second.
  Speed does not hurt, though, and a lot of code could use some improvements.
- Security has not been a primary concern so far, but it could use a lot of improvement.
- Unimplemented routines and classes are offered as stubs.

Submitting patches
------------------

- Include tests if your patch is supposed to solve a bug or add a missing feature,
  and explain clearly under which circumstances the bug happens or what was missing.
  Make sure the test fails with *zugbruecke* without your patch, while it must work
  with *ctypes* on *Wine*.
- Use **tabs** for indentation.
- No, there is no line limit. Let your editor wrap the lines for you, if you want.
- Add as many comments as you can - code-readability matters.
- The ``master`` branch is supposed to be stable - request merges into the
  ``develop`` branch instead.
- Commits are preferred to be signed (GPG). Seriously, sign your code.

Looking for work? Check *zugbruecke*'s `open issues`_ :)

.. _open issues: https://github.com/pleiszenburg/zugbruecke/issues

First time setup
----------------

- Make sure you have *Wine* 2.x and *CPython* 3.x installed.
- Download and install the `latest version of git`_.
- Configure git with your `username`_ and `email`_:

.. code:: bash

	git config --global user.name 'your name'
	git config --global user.email 'your email'

- Make sure you have a `GitHub account`_.
- Fork *zugbruecke* to your GitHub account by clicking the `Fork`_ button.
- `Clone`_ your GitHub fork locally:

.. code:: bash

	git clone https://github.com/{username}/zugbruecke
	cd zugbruecke

- Add the main repository as a remote to update later:

.. code:: bash

	git remote add pleiszenburg https://github.com/pleiszenburg/zugbruecke
	git fetch pleiszenburg

- Create a virtualenv:

.. code:: bash

	python3 -m venv env
	. env/bin/activate

- Install *zugbruecke* in editable mode with development dependencies.
  If the installation succeeds, *pytest* will say hello from a Windows path.

.. code:: bash

	make install_link

.. _GitHub account: https://github.com/join
.. _latest version of git: https://git-scm.com/downloads
.. _username: https://help.github.com/articles/setting-your-username-in-git/
.. _email: https://help.github.com/articles/setting-your-email-in-git/
.. _Fork: https://github.com/pleiszenburg/zugbruecke#fork-destination-box
.. _Clone: https://help.github.com/articles/fork-a-repo/#step-2-create-a-local-clone-of-your-fork

Useful helpers
--------------

Have a look at the ``wine-python``, ``wine-pip`` and ``wine-pytest`` commands.
They actually work as one would expect ;) If you want, you can also write
executable scripts and add ``#!/usr/bin/env wine-python`` at their top.
Check ``import os; os.name``, it will return ``nt``. Check the section on the
`Wine Python environment`_ in the documentation.

.. _`Wine Python environment`: docs/wineenv.rst
