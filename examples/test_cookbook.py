#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	examples/test_pycrosscall.py: Demonstrates ctypes examples from Cookbook R3

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
from sys import platform

if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:

	from pycrosscall import ctypes
	ctypes.windll.start_session(parameter = {'log_level': 10})

elif platform.startswith('win'):

	import ctypes

else:

	raise # TODO unsupported platform


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def divide(x, y):

	rem = ctypes.c_int()
	quot = _divide(x,y,rem)
	return quot,rem.value


# Define a special type for the 'double *' argument
class DoubleArrayType:


	def from_param(self, param):

		typename = type(param).__name__
		if hasattr(self, 'from_'+typename):
			return getattr(self, 'from_'+typename)(param)
		elif isinstance(param, ctypes.Array):
			return param
		else:
			raise TypeError("Can't convert %s" % typename)


	# Cast from array.array objects
	def from_array(self, param):

		if param.typecode != 'd':
			raise TypeError('must be an array of doubles')
		ptr, _ = param.buffer_info()
		return ctypes.cast(ptr, ctypes.POINTER(ctypes.c_double))


	# Cast from lists/tuples
	def from_list(self, param):

		val = ((ctypes.c_double)*len(param))(*param)
		return val


	from_tuple = from_list


	# Cast from a numpy array
	def from_ndarray(self, param):

		return param.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


def avg(values):

	return _avg(values, len(values))


# struct Point { }
class Point(ctypes.Structure):


	_fields_ = [
		('x', ctypes.c_double),
		('y', ctypes.c_double)
		]


class sample_class:


	def __init__(self):

		_mod = ctypes.windll.LoadLibrary('demo_dll.dll')

		# int gcd(int, int)
		gcd = _mod.cookbook_gcd
		gcd.argtypes = (ctypes.c_int, ctypes.c_int)
		gcd.restype = ctypes.c_int

		# int in_mandel(double, double, int)
		in_mandel = _mod.cookbook_in_mandel
		in_mandel.argtypes = (ctypes.c_double, ctypes.c_double, ctypes.c_int)
		in_mandel.restype = ctypes.c_int

		# int divide(int, int, int *)
		_divide = _mod.cookbook_divide
		_divide.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
		_divide.restype = ctypes.c_int

		# void avg(double *, int n)
		DoubleArray = DoubleArrayType()
		_avg = _mod.cookbook_avg
		_avg.argtypes = (DoubleArray, ctypes.c_int)
		_avg.restype = ctypes.c_double

		# double distance(Point *, Point *)
		distance = _mod.cookbook_distance
		distance.argtypes = (ctypes.POINTER(Point), ctypes.POINTER(Point))
		distance.restype = ctypes.c_double


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# RUN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	sample = sample_class()

	print(sample.gcd(35,42))
	print(sample.in_mandel(0,0,500))
	print(sample.in_mandel(2.0,1.0,500))
	print(sample.divide(42,8))
	print(sample.avg([1,2,3]))
	p1 = sample.Point(1,2)
	p2 = sample.Point(4,5)
	print(sample.distance(p1,p2))
