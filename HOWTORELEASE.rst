How to release zugbruecke
==========================

#. Merge all relevant changes into branch ``develop`` - this is where development and pre-release testing happens.

#. In branch ``develop``, run tests and examples and check that the documentation builds without errors.

	.. code:: bash

		make test

#. In branch ``develop``, add missing changes to ``CHANGES.rst`` and commit.

#. Push branch ``develop`` to GitHub.

#. Wait for feedback from Travis CI.

#. Change to branch ``master``.

#. Merge branch ``develop`` into branch ``master`` (comment ``"%s release"  % version``).

#. Push branch ``master`` to GitHub.

#. Tag branch ``master`` with ``"v_%s"  % version``.

	.. code:: bash

		git tag "v0.0.1"

#. Push the tag to Github.

	.. code:: bash

		git push origin --tags

#. Build and sign packages.

	.. code:: bash

		make release

#. Upload package to ``pypitest`` and review result.

	.. code:: bash

		make upload_test

#. Upload package to ``pypi``.

	.. code:: bash

		make upload

#. Change to branch ``develop``.

#. In branch ``develop``, bump the package version in ``setup.py`` by changing the ``version`` string.

#. In ``CHANGES.rst``, indicate that a new development cycle has started.

#. Commit to branch ``develop``.

#. Push branch ``develop`` to GitHub.
