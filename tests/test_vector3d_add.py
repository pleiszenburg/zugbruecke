# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_vector3d_add.py: Tests pointer to struct type return value

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017-2018 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke as ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class vector3d(ctypes.Structure):


	_fields_ = [
		('x', ctypes.c_int16),
		('y', ctypes.c_int16),
		('z', ctypes.c_int16)
		]


class sample_class_a:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		# vector3d *distance(vector3d *, vector3d *)
		self.__vector3d_add__ = self.__dll__.vector3d_add
		self.__vector3d_add__.argtypes = (ctypes.POINTER(vector3d), ctypes.POINTER(vector3d))
		self.__vector3d_add__.restype = ctypes.POINTER(vector3d)


	def vector3d_add(self, v1, v2):

		def struct_from_dict(in_dict):
			return vector3d(*tuple(in_dict[key] for key in ['x', 'y', 'z']))
		def dict_from_struct(in_struct):
			return {key: getattr(in_struct.contents, key) for key in ['x', 'y', 'z']}

		return dict_from_struct(self.__vector3d_add__(
			struct_from_dict(v1), struct_from_dict(v2)
			))


class sample_class_b:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		self.__vector3d_add_array__ = self.__dll__.vector3d_add_array
		self.__vector3d_add_array__.argtypes = (ctypes.POINTER(vector3d), ctypes.c_int16)
		self.__vector3d_add_array__.restype = ctypes.POINTER(vector3d)
		self.__vector3d_add_array__.memsync = [
			{
				'p': [0],
				'l': [1],
				't': 'vector3d'
				}
			]


	def vector3d_add_array(self, v):

		length = len(v)

		def dict_from_struct(in_struct):
			return {key: getattr(in_struct.contents, key) for key in ['x', 'y', 'z']}

		v_ctypes = (vector3d * length)()
		for i in range(length):
			for key in v[i].keys():
				setattr(v_ctypes[i], key, v[i][key])

		return dict_from_struct(self.__vector3d_add_array__(
			ctypes.cast(ctypes.pointer(v_ctypes), ctypes.POINTER(vector3d)), length
			))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_vector3d_add():

	v1 = {'x': 5, 'y': 7, 'z': 2}
	v2 = {'x': 1, 'y': 9, 'z': 8}
	added = {'x': 6, 'y': 16, 'z': 10}

	sample = sample_class_a()

	assert added == sample.vector3d_add(v1, v2)


def test_vector3d_add_array():

	v = [
		{'x': 5, 'y': 7, 'z': 2},
		{'x': 1, 'y': 9, 'z': 8}
		]
	added = {'x': 6, 'y': 16, 'z': 10}

	sample = sample_class_b()

	assert added == sample.vector3d_add_array(v)
