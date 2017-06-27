How to release zugbruecke
==========================

#. Merge all relevant changes into branch ``develop`` - this is where development and pre-release testing happens.

#. In branch ``develop``, run tests and examples ...

#. In branch ``develop``, adjust package version in ``setup.py`` by changing the ``version`` string.

#. Push branch ``develop`` to GitHub.

#. Change to branch ``master``.

#. Merge branch ``develop`` into branch ``master`` and push it to GitHub.

#. Tag branch ``master`` with ``"v_%s"  % version``.

	.. code:: bash

		git tag "v0.0.1"

#. Push the tag to Github.

	.. code:: bash

		git push origin --tags

#. Upload package to ``pypitest`` and review result.

	.. code:: bash

		python setup.py sdist upload -r pypitest

#. Upload package to ``pypi``.

	.. code:: bash

		python setup.py sdist upload -r pypi
