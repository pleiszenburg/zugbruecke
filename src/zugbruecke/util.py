# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/util.py: ctypes.util for POSIX, hacked for DLL compatibility

	Required to run on platform / side: [UNIX]

	Based on:
	https://github.com/python/cpython/blob/master/Lib/ctypes/util.py
	https://github.com/python/cpython/commit/a76f014278bd1643e93fdfa9e88f9414ce8354a6

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

import subprocess
from ctypes.util import find_library as __find_library_unix__


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CROSS-PLATFORM FIND LIBRARY ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def find_msvcrt():
	"""
	Likely useless and will return None, see https://bugs.python.org/issue23606
	Offered for full compatibility, though.
	"""

	# Compile Python command for wine-python
	command = '"from ctypes.util import find_msvcrt; print(find_msvcrt())"'

	# Start wine-python
	winepython_p = subprocess.Popen(
		'wine-python -c' + command,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		shell = True
		)

	# Get stdout and stderr
	winepython_out, winepython_err = winepython_p.communicate()

	# Change encoding
	winepython_out = winepython_out.decode(encoding = 'UTF-8').strip()

	# Handle None values
	if winepython_out in ['', 'None']:
		winepython_out = None

	return winepython_out


def find_library(name):

	# Result is none by definition
	result = None

	# Is this a DLL for sure?
	is_dll = (name.strip().lower()[-4:] == '.dll')

	# If this is (likely) not a DLL, look for it on Unix side
	if not is_dll:
		result = __find_library_unix__(name)

	# If library was not found on Unix side or is DLL for sure
	if result is None or is_dll:

		# Compile Python command for wine-python
		command = '"from ctypes.util import find_library; print(find_library(\'%s\'))"' % name

		# Start wine-python
		winepython_p = subprocess.Popen(
			'wine-python -c' + command,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			shell = True
			)

		# Get stdout and stderr
		winepython_out, winepython_err = winepython_p.communicate()

		# Change encoding
		winepython_out = winepython_out.decode(encoding = 'UTF-8').strip()

		# Check result, handle None value
		if winepython_out not in ['', 'None']:
			result = winepython_out

	return result
