# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_apply_filter_to_image.py: Demonstrates memsync on callback routines

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

# import pytest

from sys import platform
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke.ctypes as ctypes
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

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		filter_func_type = ctypes.WINFUNCTYPE(ctypes.c_int16, ctypes.POINTER(image_data))
		filter_func_type.memsync = [
			{
				'p': [0, 'data'],
				'l': ([0, 'width'], [0, 'height']),
				'f': 'lambda x, y: x * y',
				't': 'c_int16'
				}
			]

		self.__apply_filter_to_image__ = self.__dll__.apply_filter_to_image
		self.__apply_filter_to_image__.argtypes = (
			ctypes.POINTER(image_data),
			ctypes.POINTER(image_data),
			filter_func_type
			)
		self.__apply_filter_to_image__.memsync = [
			{
				'p': [0, 'data'],
				'l': ([0, 'width'], [0, 'height']),
				'f': 'lambda x, y: x * y',
				't': 'c_int16'
				},
			{
				'p': [1, 'data'],
				'l': ([1, 'width'], [1, 'height']),
				'f': 'lambda x, y: x * y',
				't': 'c_int16'
				}
			]

		@filter_func_type
		def filter_edge_detection(in_buffer):

			filter_matrix = [
				[0,  1, 0],
				[1, -4, 1],
				[0,  1, 0]
				]

			width = in_buffer.contents.width
			height = in_buffer.contents.height

			assert width == 3 and height == 3

			in_matrix = self.array_to_matrix(
				ctypes.cast(
					in_buffer.contents.data,
					ctypes.POINTER(ctypes.c_int16 * (width * height))
					).contents[:],
				width,
				height
				)

			out_value = 0
			for matrix_line, filter_line in zip(in_matrix, filter_matrix):
				out_value += sum([a * b for a, b in zip(matrix_line, filter_line)])

			return out_value

		self.__filter_edge_detection__ = filter_edge_detection


	def apply_filter_to_image(self, in_image):

		width = len(in_image[0])
		height = len(in_image)

		in_image_ctypes = image_data()
		out_image_ctypes = image_data()

		in_image_ctypes.width = ctypes.c_int16(width)
		in_image_ctypes.height = ctypes.c_int16(height)
		in_image_ctypes.data = ctypes.cast(
			ctypes.pointer((ctypes.c_int16 * (width * height))(*self.matrix_to_array(in_image))),
			ctypes.POINTER(ctypes.c_int16)
			)

		self.__apply_filter_to_image__(
			ctypes.pointer(in_image_ctypes),
			ctypes.pointer(out_image_ctypes),
			self.__filter_edge_detection__
			)

		return self.array_to_matrix(
			ctypes.cast(out_image_ctypes.data, ctypes.POINTER(ctypes.c_int16 * (width * height))).contents[:],
			width,
			height
			)


	def array_to_matrix(self, in_array, a_width, a_height):
		return [in_array[(i * a_width):((i + 1) * a_width)] for i in range(a_height)]


	def matrix_to_array(self, in_matrix):
		return [item for line_list in in_matrix for item in line_list]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_apply_filter_to_image():

	sample = sample_class()

	result = sample.apply_filter_to_image([
		[253, 252, 254, 243, 243, 230, 251, 247, 255, 254],
		[252, 254, 239, 144, 253, 247, 220, 252, 235, 255],
		[252, 246, 166, 123, 168, 237, 244, 252, 235, 255],
		[255, 228, 176, 103, 138, 250, 228, 252, 252, 252],
		[219, 217, 146, 152, 146, 170, 250, 253, 246, 243],
		[254, 162, 116, 128, 133, 154, 247, 255, 244, 253],
		[224, 116, 136, 154, 129, 147, 189, 248, 254, 205],
		[192, 105, 117, 138, 148, 101, 111, 248, 248, 239],
		[254, 231, 168, 153, 124, 113, 111, 207, 238, 245],
		[216, 255, 251, 235, 247, 227, 175, 182, 249, 248]
		])

	assert [
		[-508, -247, -282, -331, -246, -179, -307, -230, -284, -506],
		[-249,  -27, -138,  282, -210,  -48,  114,  -54,   57, -276],
		[-255,  -84,  120,   89,   79,  -39,  -39,  -25,   54, -278],
		[-321,  -18,  -61,  177,  115, -227,   84,  -23,  -23, -258],
		[-150, -113,   77,  -85,    9,  120, -102,   -9,    8, -221],
		[-411,   55,  108,   43,   25,   81, -140,  -28,   32, -320],
		[-334,  163,  -41,  -85,   66,  -15,   -3,  -46,  -71,  -74],
		[-185,  236,   79,   20, -100,  115,  205, -178,  -13, -258],
		[-377, -142,   80,   53,  165,  111,  162,  -49,   -3, -255],
		[-355, -322, -346, -289, -402, -373, -180,  -97, -328, -498]
		] == result
