# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_apply_filter_to_image.py: Demonstrates memsync on callback routines

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

class image_data(ctypes.Structure):


	_fields_ = [
		('data', ctypes.POINTER(ctypes.c_int16)),
		('width', ctypes.c_int16),
		('height', ctypes.c_int16)
		]


class sample_class:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('demo_dll.dll') # tests/

		filter_func_type = ctypes.WINFUNCTYPE(ctypes.c_int16, ctypes.POINTER(image_data))

		self.__apply_filter_to_image__ = self.__dll__.apply_filter_to_image
		self.__apply_filter_to_image__.argtypes = (
			ctypes.POINTER(image_data),
			ctypes.POINTER(image_data),
			filter_func_type
			)

		@filter_func_type
		def filter_sharpen(in_buffer):
			print('BING! %s' % str(in_buffer))
			return 1

		self.__filter_sharpen__ = filter_sharpen


	def apply_filter_to_image(self, in_image):

		def matrix_to_array(in_matrix):
			return [item for line_list in in_matrix for item in line_list]

		def array_to_matrix(in_array, a_width, a_height):
			return [in_array[i:i+a_width] for i in range(a_height)]

		width = len(in_image[0])
		height = len(in_image)

		in_image_ctypes = image_data()
		out_image_ctypes = image_data()

		in_image_ctypes.width = ctypes.c_int16(width)
		in_image_ctypes.height = ctypes.c_int16(height)
		in_image_ctypes.data = ctypes.cast(
			ctypes.pointer((ctypes.c_int16 * (width * height))(*matrix_to_array(in_image))),
			ctypes.POINTER(ctypes.c_int16)
			)

		self.__apply_filter_to_image__(
			ctypes.pointer(in_image_ctypes),
			ctypes.pointer(out_image_ctypes),
			self.__filter_sharpen__
			)

		return array_to_matrix(
			ctypes.cast(out_image_ctypes.data, ctypes.POINTER(ctypes.c_int16 * (width * height))).contents[:],
			width, height
			)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_apply_filter_to_image():

	sample = sample_class()

	assert [
		[1, 1, 1, 1, 1],
		[1, 1, 1, 1, 1],
		[1, 1, 1, 1, 1],
		[1, 1, 1, 1, 1],
		[1, 1, 1, 1, 1]
		] == sample.apply_filter_to_image([
		[0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0]
		])
