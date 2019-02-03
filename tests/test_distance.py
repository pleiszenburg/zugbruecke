# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_distance.py: Tests by value struct type passing and return value

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import pytest

from sys import platform
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke.ctypes as ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# struct Point { }
class Point(ctypes.Structure):


	_fields_ = [
		('x', ctypes.c_double),
		('y', ctypes.c_double)
		]


class sample_class:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		# double distance(Point *, Point *)
		self.distance = self.__dll__.cookbook_distance
		self.distance.argtypes = (ctypes.POINTER(Point), ctypes.POINTER(Point))
		self.distance.restype = ctypes.c_double

		# double *distance_pointer(Point *, Point *)
		self.__distance_pointer__ = self.__dll__.cookbook_distance_pointer
		self.__distance_pointer__.argtypes = (ctypes.POINTER(Point), ctypes.POINTER(Point))
		self.__distance_pointer__.restype = ctypes.POINTER(ctypes.c_double)


	def distance_pointer(self, in1, in2):

		return self.__distance_pointer__(in1, in2).contents.value


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_distance():

	sample = sample_class()

	p1 = Point(1, 2)
	p2 = Point(4, 5)

	assert pytest.approx(4.242640687119285, 0.0000001) == sample.distance(p1, p2)


def test_distance_pointer():

	sample = sample_class()

	p1 = Point(1, 2)
	p2 = Point(4, 5)

	assert pytest.approx(4.242640687119285, 0.0000001) == sample.distance_pointer(p1, p2)
