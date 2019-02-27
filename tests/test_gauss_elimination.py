# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_gauss_elimination.py: Tests 2D fixed length arrays w/ floats

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

# import pytest

from sys import platform
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke.ctypes as ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class sample_class:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		# void gauss_elimination(float [3][4] *)
		self.__gauss_elimination__ = self.__dll__.gauss_elimination
		self.__gauss_elimination__.argtypes = (
			ctypes.POINTER(ctypes.c_float * 4 * 3),
			ctypes.POINTER(ctypes.c_float * 3)
			)


	def gauss_elimination(self, A):

		N = 3
		if len(A) != N or len(A[0]) != N + 1:
			raise # TODO

		x = [0 for eq in range(N)]
		_A = (ctypes.c_float * (N + 1) * N)(*(tuple(eq) for eq in A))
		_x = (ctypes.c_float * N)(*tuple(x))
		self.__gauss_elimination__(ctypes.pointer(_A), ctypes.pointer(_x))
		for index, eq in enumerate(A):
			eq[:] = _A[index][:]
		x[:] = _x[:]

		return x


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_gauss_elimination():

	sample = sample_class()

	eq_sys = [
		[1, 2, 3, 2],
		[1, 1, 1, 2],
		[3, 3, 1, 0]
		]
	eq_sys_solution = sample.gauss_elimination(eq_sys)

	assert (
		[5.0, -6.0, 3.0], [[1.0, 2.0, 3.0, 2.0], [0.0, -1.0, -2.0, 0.0], [0.0, 0.0, -2.0, -6.0]]
		) == (eq_sys_solution, eq_sys)
