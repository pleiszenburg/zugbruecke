How to release pycrosscall
==========================

#. Merge all relevant changes into branch ``develop`` - this is where development and pre-release testing happens.

#. In branch ``develop``, adjust package version in ``setup.py`` by changing the ``version`` string.

#. Push branch ``develop`` to GitHub.

#. Change to branch ``master``.

#. Merge branch ``develop`` into branch ``master`` and push it to GitHub.

#. Tag branch ``master`` with ``pycrosscall_%s`` % version.

    git tag "pycrosscall_0.0.1"

#. Push the tag to Github.

    git push origin --tags

#. Upload package to ``pypitest`` and review result.

    python setup.py sdist upload -r pypitest

#. Upload package to ``pypi``.

    python setup.py sdist upload -r pypi
