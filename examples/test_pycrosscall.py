
import sys
import os
import time
from sys import platform

if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:

	from pycrosscall import ctypes
	ctypes.windll.start_session(parameter = {'log_level': 10})

elif platform.startswith('win'):

	import ctypes

else:

	raise # TODO unsupported platform

_call_demo_routine_ = ctypes.windll.LoadLibrary('demo_dll.dll').simple_demo_routine
print('DLL and routine loaded!')

_call_demo_routine_.argtypes = [
	ctypes.c_float,
	ctypes.c_float
	]
print('Set argument types!')

_call_demo_routine_.restype = ctypes.c_float
print('Set return value type!')

return_value = _call_demo_routine_(20.0, 1.07)
print('Called!')
try:
	print('Got "%f".' % return_value)
except:
	print('Got no return value!')
