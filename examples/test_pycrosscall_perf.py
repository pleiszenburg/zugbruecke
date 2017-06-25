#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	examples/test_pycrosscall_perf.py: Performance measurements

	Required to run on platform / side: [UNIX, WINE]

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

import sys
import os
import time
import timeit
from sys import platform

if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:

	from pycrosscall import ctypes
	ctypes.windll.start_session(parameter = {'log_level': 0})

elif platform.startswith('win'):

	import ctypes

else:

	raise # TODO unsupported platform


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# RUN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

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
	print('[TIME] %f' % t.timeit(number = 100000))
