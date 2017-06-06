
import sys
import os
import time

pycrosscall_path = os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.insert(0, pycrosscall_path)

# import pycrosscall
# pycrosscall_session = pycrosscall.session()

from pycrosscall import ctypes
_call_demo_routine_ = ctypes.windll.LoadLibrary('demo_dll.dll') # .demo_routine
print('Loaded!')

time.sleep(8)
