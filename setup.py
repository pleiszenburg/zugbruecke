# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	setup.py: Used for package distribution

	Required to run on platform / side: [UNIX]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/s-m-e/pycrosscall/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from distutils.core import setup
import os
from glob import glob


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Bump version HERE!
version = '0.0.4'


# List all versions of Python which are supported
confirmed_python_versions = [
	('Programming Language :: Python :: %s' % x)
	for x in '3.5 3.6'.split()
	]


# Fetch readme file
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
	long_description = f.read()


setup(
	name = 'pycrosscall',
	packages = ['pycrosscall'],
	version = version,
	description = 'Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD',
	long_description = long_description,
	author = 'Sebastian M. Ernst',
	author_email = 'ernst@pleiszenburg.de',
	url = 'https://github.com/s-m-e/pycrosscall',
	download_url = 'https://github.com/s-m-e/pycrosscall/archive/pycrosscall_%s.tar.gz' % version,
	license = 'LGPLv2',
	keywords = ['ctypes', 'wine'],
	scripts = glob(os.path.join('scripts', '*')),
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
