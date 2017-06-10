
import sys
import os
import time
import timeit
from sys import platform

pycrosscall_path = os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.insert(0, pycrosscall_path)

from pycrosscall import ctypes
if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:
	ctypes.windll.start_session(parameter = {'log_level': 0})

_call_demo_routine_ = ctypes.windll.LoadLibrary('demo_dll.dll').simple_demo_routine
_call_demo_routine_.argtypes = [
	ctypes.c_float,
	ctypes.c_float
	]
_call_demo_routine_.restype = ctypes.c_float

timeit.timeit('return_value = _call_demo_routine_(20.0, 1.07)', number = 10)
