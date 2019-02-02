# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_sqrt_int.py: Test function with single parameter

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

from sys import platform
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke as ctypes
elif platform.startswith('win'):
	import ctypes

import pytest


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class sample_class:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		self.__replace_r__ = self.__dll__.replace_letter_in_null_terminated_string_r
		self.__replace_r__.argtypes = (
			ctypes.POINTER(ctypes.POINTER(ctypes.c_char)), # Generate pointer to char manually
			ctypes.c_char,
			ctypes.c_char
			)
		self.__replace_r__.memsync = [
			{
				'p': [0, -1],
				'n': True
				}
			]


	def replace_r(self, in_string, old_letter, new_letter):

		string_buffer = (ctypes.c_char_p * 1)(in_string.encode('utf-8'))
		string_buffer_p = ctypes.cast(
			string_buffer,
			ctypes.POINTER(ctypes.POINTER(ctypes.c_char))
			)

		self.__replace_r__(
			string_buffer_p,
			old_letter.encode('utf-8'),
			new_letter.encode('utf-8')
			)

		return string_buffer[:][0].decode('utf-8')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.mark.xfail(strict = False, reason = 'not yet implemented')
def test_r_strsxp():

	sample = sample_class()
	assert 'zetegehube' == sample.replace_r('zategahuba', 'a', 'e')
