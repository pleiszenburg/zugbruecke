
import sys
import os
import time

pycrosscall_path = os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.insert(0, pycrosscall_path)

from pycrosscall import ctypes

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
	pass

time.sleep(8)
