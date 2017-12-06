# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	setup.py: Used for package distribution

	Required to run on platform / side: [UNIX]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

from setuptools import (
	find_packages,
	setup
	)
import os
from glob import glob
from sys import platform


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Bump version HERE!
_version_ = '0.0.7'


# List all versions of Python which are supported
confirmed_python_versions = [
	('Programming Language :: Python :: %s' % x)
	for x in '3.4 3.5 3.6'.split()
	]


# Fetch readme file
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
	long_description = f.read()


# Just in case someone is actually running this on Windows ...
if platform.startswith('win'):
	raise SystemExit('You are already running Windows. No need for this package!')


setup(
	name = 'zugbruecke',
	packages = find_packages('src'),
	package_dir = {'': 'src'},
	version = _version_,
	description = 'Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD',
	long_description = long_description,
	author = 'Sebastian M. Ernst',
	author_email = 'ernst@pleiszenburg.de',
	url = 'https://github.com/pleiszenburg/zugbruecke',
	download_url = 'https://github.com/pleiszenburg/zugbruecke/archive/v%s.tar.gz' % _version_,
	license = 'LGPLv2',
	keywords = ['ctypes', 'wine'],
	scripts = glob(os.path.join('scripts', '*')),
	include_package_data = True,
	install_requires = [],
	extras_require = {'dev': [
		'pytest',
		'python-language-server',
		'setuptools',
		'Sphinx',
		'sphinx_rtd_theme',
		'twine',
		'wheel'
		]},
	zip_safe = False,
	entry_points = {},
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
		'Operating System :: MacOS',
		'Operating System :: POSIX :: BSD',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python :: 3'
		] + confirmed_python_versions + [
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: Implementation :: CPython',
		'Topic :: Scientific/Engineering',
		'Topic :: Software Development',
		'Topic :: System :: Operating System',
		'Topic :: System :: Operating System Kernels',
		'Topic :: Utilities'
		]
)
