
import sys
import os
import time

pycrosscall_path = os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.insert(0, pycrosscall_path)

from pycrosscall import ctypes
_call_demo_routine_ = ctypes.windll.LoadLibrary('demo_dll.dll').simple_demo_routine
print('Loaded!')
_call_demo_routine_(20)
print('Called!')

time.sleep(8)
