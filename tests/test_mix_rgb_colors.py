# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_mix_rgb_colors.py: Tests 1D fixed length arrays with ints

	Required to run on platform / side: [UNIX, WINE]

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

# import pytest

from sys import platform
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke as ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class sample_class:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		# void mix_rgb_colors(int8_t [3], int8_t [3], int8_t *)
		self.__mix_rgb_colors__ = self.__dll__.mix_rgb_colors
		self.__mix_rgb_colors__.argtypes = (
			ctypes.c_ubyte * 3, ctypes.c_ubyte * 3, ctypes.POINTER(ctypes.c_ubyte * 3)
			)


	def mix_rgb_colors(self, color_a, color_b):

		color_type = ctypes.c_ubyte * 3
		ctypes_color_a = color_type(*tuple(color_a))
		ctypes_color_b = color_type(*tuple(color_b))
		mixed_color = color_type()
		self.__mix_rgb_colors__(
			ctypes_color_a, ctypes_color_b, ctypes.pointer(mixed_color)
			)
		return mixed_color[:]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_mix_rgb_colors():

	sample = sample_class()

	assert [45, 35, 30] == sample.mix_rgb_colors([10, 20, 40], [80, 50, 20])
