
import sys
import os
import time
import timeit
from sys import platform

if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:

	# HACK
	pycrosscall_path = os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
	sys.path.insert(0, pycrosscall_path)

	from pycrosscall import ctypes
	ctypes.windll.start_session(parameter = {'log_level': 0})

elif platform.startswith('win'):

	import ctypes

else:

	raise # TODO unsupported platform

_simple_demo_routine_ = ctypes.windll.LoadLibrary('demo_dll.dll').simple_demo_routine
_simple_demo_routine_.argtypes = [
	ctypes.c_float,
	ctypes.c_float
	]
_simple_demo_routine_.restype = ctypes.c_float
return_value = _simple_demo_routine_(20.0, 1.07) # Run once, so everything is set up
return_value = _simple_demo_routine_(20.0, 1.07) # Run twice for checks ...

def test_simple_demo_routine():
	return_value = _simple_demo_routine_(20.0, 1.07)

t = timeit.Timer(
	'test_simple_demo_routine()',
	setup = "from __main__ import test_simple_demo_routine"
	)
print('[TIME] %f' % t.timeit(number = 10000))
