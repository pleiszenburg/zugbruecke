# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    setup.py: Used for package distribution

    Required to run on platform / side: [UNIX]

    Copyright (C) 2017-2021 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os

from setuptools import find_packages, setup

from docs.version import get_version

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

__version__ = get_version()

# List all versions of Python which are supported
python_minor_min = 6
python_minor_max = 10
confirmed_python_versions = [
    "Programming Language :: Python :: 3.{MINOR:d}".format(MINOR=minor)
    for minor in range(python_minor_min, python_minor_max + 1)
]

# Fetch readme file
with open(os.path.join(os.path.dirname(__file__), "README.rst")) as f:
    long_description = f.read()

# Fetch test requirements
with open(os.path.join(os.path.dirname(__file__), "requirements_test.txt")) as f:
    requirements_test = [
        rq.strip() for rq in f.read().split("\n") if len(rq.strip()) > 0
    ]

setup(
    name="zugbruecke",
    packages=find_packages("src"),
    package_dir={"": "src"},
    version=__version__,
    description="Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD",
    long_description=long_description,
    author="Sebastian M. Ernst",
    author_email="ernst@pleiszenburg.de",
    url="https://github.com/pleiszenburg/zugbruecke",
    download_url="https://github.com/pleiszenburg/zugbruecke/archive/v%s.tar.gz"
    % __version__,
    license="LGPLv2",
    keywords=["ctypes", "wine"],
    scripts=[],
    include_package_data=True,
    python_requires=">=3.{MINOR:d}".format(MINOR=python_minor_min),
    install_requires=["wenv"],
    extras_require={
        "dev": requirements_test
        + [
        "Jinja2", "python-lsp-server[all]", "setuptools",
        "Sphinx", "sphinx_rtd_theme", "sphinx-autodoc-typehints", "myst-parser",
        "twine", "wheel",
        ],
        "certifi": ["certifi"],
    },
    zip_safe=False,
    entry_points={},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ]
    + confirmed_python_versions
    + [
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: System :: Operating System",
        "Topic :: System :: Operating System Kernels",
        "Topic :: Utilities",
    ],
)
