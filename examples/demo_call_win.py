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
			ctypes.c_char_p,
			ctypes.c_int,
			ctypes.POINTER(type_test_struct)
			]
		
		# Define return datatype
		self._call_demo_routine_.restype = ctypes.c_void_p
	
	
	def call(self, p_str1, p_str2, p_L1):
		
		try:
		
			# Call routine in DLL
			self._call_demo_routine_(
				p_str1_buff, 
				p_str1_len, 
				p_str2_buff, 
				p_str2_len, 
				ctypes.byref(p_L1)
				)
			
			return True
			
		except:
			
			return False

