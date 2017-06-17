#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	examples/demo_call_win.py: Project target, run this file on Unix-side

	Required to run on platform / side: [WINE]

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


import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# STRUCT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class type_test_struct(ctypes.Structure):

	_fields_ = [
		('el_char', ctypes.c_char),
		('el_int8t', ctypes.c_int8),
		('el_int16t', ctypes.c_int16),
		('el_float', ctypes.c_float),
		('el_double', ctypes.c_double),
		('el_int8t_4', ctypes.c_int8 * 4),
		('el_int8t_2x3', ctypes.c_int8 * 2 * 3)
		]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CALLER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class demo_routine_caller_class():

	def __init__(self):

		# Generate reference on routine in DLL
		self._call_demo_routine_ = ctypes.windll.LoadLibrary('demo_dll.dll').complex_demo_routine

		# Define parameter datatypes
		self._call_demo_routine_.argtypes = [
			ctypes.POINTER(ctypes.c_char),
			ctypes.c_int,
			ctypes.POINTER(type_test_struct)
			]

		# Define return datatype
		self._call_demo_routine_.restype = ctypes.c_void_p


	def call(self, param_char, param_int, param_type_test):

		# Call routine in DLL
		self._call_demo_routine_(
			ctypes.byref(param_char),
			param_int,
			ctypes.byref(param_type_test)
			)

		print('Called!')
		return True


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAKE A CALL
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	# Initialize some test parameters
	sample_param_char = ctypes.c_char(7)
	sample_param_int = ctypes.c_int(42)
	sample_type_test = type_test_struct()
	sample_type_test.el_char = ctypes.c_char(5)
	sample_type_test.el_int8t = ctypes.c_int8(17)
	sample_type_test.el_int16t = ctypes.c_int16(25874)
	sample_type_test.el_float = ctypes.c_float(2.4)
	sample_type_test.el_double = ctypes.c_double(8.598e31)
	el_int8t_4 = [1, 2, 3, 4]
	sample_type_test.el_int8t_4 = (ctypes.c_int8 * len(el_int8t_4))(*el_int8t_4)
	el_int8t_2x3 = [[1, 2], [3, 4], [5, 6]]
	sample_type_test.el_int8t_2x3 = (ctypes.c_int8 * len(el_int8t_2x3[0]) * len(el_int8t_2x3))(*(tuple(i) for i in el_int8t_2x3))

	# Initialize caller
	demo_routine_caller = demo_routine_caller_class()

	# Call
	demo_routine_caller.call(sample_param_char, sample_param_int, sample_type_test)
