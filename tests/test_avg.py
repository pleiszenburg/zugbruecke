# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_avg.py: Test custom datatype argument passing as pointer

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

import pytest

from sys import platform
if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:
	from zugbruecke import ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Define a special type for the 'double *' argument
class DoubleArrayType:


	def from_param(self, param):

		typename = type(param).__name__
		if hasattr(self, 'from_' + typename):
			return getattr(self, 'from_' + typename)(param)
		elif isinstance(param, ctypes.Array):
			return param
		else:
			raise TypeError('Can\'t convert %s' % typename)


	# Cast from array.array objects
	def from_array(self, param):

		if param.typecode != 'd':
			raise TypeError('must be an array of doubles')
		ptr, _ = param.buffer_info()
		return ctypes.cast(ptr, ctypes.POINTER(ctypes.c_double))


	# Cast from lists/tuples
	def from_list(self, param):

		val = ((ctypes.c_double)*len(param))(*param)
		return val


	from_tuple = from_list


	# Cast from a numpy array
	def from_ndarray(self, param):

		return param.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


class sample_class:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		# void avg(double *, int n)
		DoubleArray = DoubleArrayType()
		self.__avg__ = self.__dll__.cookbook_avg
		self.__avg__.memsync = [ # Regular ctypes on Windows should ignore this statement
			{
				'p': [0], # "path" to argument containing the pointer
				'l': [1], # "path" to argument containing the length
				'_t': ctypes.c_double, # type of argument (optional, default char/byte): sizeof(type) * length == bytes
				'_c': DoubleArray # custom datatype
				}
			]
		self.__avg__.argtypes = (DoubleArray, ctypes.c_int)
		self.__avg__.restype = ctypes.c_double


	def avg(self, values):

		return self.__avg__(values, len(values))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_avg():

	sample = sample_class()

	assert pytest.approx(2.5, 0.0000001) == sample.avg([1, 2, 3, 4])
