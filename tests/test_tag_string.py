# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_tag_string.py: Demonstrates memory allocation by DLL

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017-2018 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

# import pytest

from sys import platform
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke as ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class sample_class_a:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		self.__tag_string__ = self.__dll__.tag_string_a
		self.__tag_string__.argtypes = (
			ctypes.POINTER(ctypes.c_char),
			ctypes.c_void_p
			)
		self.__tag_string__.memsync = [
			{
				'p': [0],
				'l': ([0],),
				'f': 'lambda x: ctypes.sizeof(x)'
				},
			{
				'p': [1, -1],
				'l': ([0],),
				'f': 'lambda x: ctypes.sizeof(x) + 2'
				}
			]


	def tag_string(self, in_string):

		in_buffer = ctypes.create_string_buffer(in_string.encode('utf-8'))
		out_buffer = ctypes.pointer(ctypes.c_void_p())

		self.__tag_string__(in_buffer, out_buffer)

		return ctypes.cast(
			out_buffer.contents,
			ctypes.POINTER(ctypes.c_char * (len(in_buffer) + 2))
			).contents[:].decode('utf-8').rstrip('\0')


class sample_class_b:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		self.__tag_string__ = self.__dll__.tag_string_b
		self.__tag_string__.argtypes = (
			ctypes.POINTER(ctypes.c_char),
			ctypes.c_void_p
			)
		self.__tag_string__.memsync = [
			{
				'p': [0],
				'n': True
				},
			{
				'p': [1, -1],
				'n': True
				}
			]


	def tag_string(self, in_string):

		in_buffer = ctypes.create_string_buffer(in_string.encode('utf-8'))
		out_buffer = ctypes.pointer(ctypes.c_void_p())

		self.__tag_string__(in_buffer, out_buffer)

		return ctypes.cast(
			out_buffer.contents,
			ctypes.POINTER(ctypes.c_char * (len(in_buffer) + 2))
			).contents[:].decode('utf-8').rstrip('\0')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_tag_string():

	sample = sample_class_a()

	assert '<html>' == sample.tag_string('html')


def test_tag_string_serverside_length_computation():

	sample = sample_class_b()

	assert '<body>' == sample.tag_string('body')
