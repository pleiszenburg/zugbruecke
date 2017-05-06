# -*- coding: utf-8 -*-


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
		self._call_demo_routine_ = ctypes.windll.LoadLibrary('demo_dll.dll').demo_routine
		
		# Define parameter datatypes
		self._call_demo_routine_.argtypes = [
			ctypes.c_char_p,
			ctypes.c_int,
			ctypes.POINTER(type_test_struct)
			]
		
		# Define return datatype
		self._call_demo_routine_.restype = ctypes.c_void_p
	
	
	def call(self, param_char_p, param_int, param_type_test):
		
		try:
		
			# Call routine in DLL
			self._call_demo_routine_(
				param_char_p, 
				param_int, 
				ctypes.byref(param_type_test)
				)
			
			return True
			
		except:
			
			return False


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAKE A CALL
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
	
	# Initialize caller
	demo_routine_caller = demo_routine_caller_class()
	
	# Initialize some test parameters
	sample_param_char_p = 7
	sample_param_int = 42
	sample_type_test = type_test_struct()
	sample_type_test.el_char = 5
	sample_type_test.el_int8t = 17
	sample_type_test.el_int16t = 25874
	sample_type_test.el_float = 2.4
	sample_type_test.el_double = 8.598e31
	el_int8t_4 = [1, 2, 3, 4]
	sample_type_test.el_int8t_4 = (ctypes.c_int8 * len(el_int8t_4))(*el_int8t_4)
	el_int8t_2x3 = [[1, 2], [3, 4], [5, 6]]
	sample_type_test.el_int8t_2x3 = (ctypes.c_int8 * len(el_int8t_2x3[0]) * len(el_int8t_2x3))(*(tuple(i) for i in el_int8t_2x3))
	
	# Call
	demo_routine_caller.call(sample_param_char_p, sample_param_int, sample_type_test)

