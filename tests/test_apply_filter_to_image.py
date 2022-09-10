# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_apply_filter_to_image.py: Demonstrates memsync on callback routines

    Required to run on platform / side: [UNIX, WINE]

    Copyright (C) 2017-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
# C
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

HEADER = """
typedef struct image_data {
	int16_t *data;
	int16_t width;
	int16_t height;
} image_data;

typedef int16_t {{ SUFFIX }} (*filter_func_type)(image_data *section);

{{ PREFIX }} void {{ SUFFIX }} apply_filter_to_image(
	image_data *in_image,
	image_data *out_image,
	filter_func_type filter_func
	);

int16_t _coordinates_in_image_(
	image_data *in_image, int16_t x, int16_t y
	);

int16_t _image_pixel_get_(
	image_data *in_image, int16_t x, int16_t y
	);

void _image_pixel_set_(
	image_data *in_image, int16_t x, int16_t y, int16_t value
	);

void _image_copy_segment_to_buffer_(
	image_data *in_image, image_data *in_buffer, int16_t x, int16_t y
	);
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} apply_filter_to_image(
	image_data *in_image,
	image_data *out_image,
	filter_func_type filter_func
	)
{

	int16_t i, j;
	const int16_t F_W = 3;
	const int16_t F_H = 3;
	const int16_t F_W_off = F_W / 2;
	const int16_t F_H_off = F_H / 2;

	out_image->data = malloc(sizeof(int16_t) * in_image->width * in_image->height);
	out_image->width = in_image->width;
	out_image->height = in_image->height;

	image_data *buffer = malloc(sizeof(image_data));
	buffer->data = malloc(sizeof(int16_t) * F_W * F_H);
	buffer->width = F_W;
	buffer->height = F_H;

	for(i = 0; i < in_image->width; i++)
	{
		for(j = 0; j < in_image->height; j++)
		{
			_image_copy_segment_to_buffer_(in_image, buffer, i - F_W_off, j - F_H_off);
			_image_pixel_set_(out_image, i, j, filter_func(buffer));
		}
	}

	free(buffer->data);
	free(buffer);

}

int16_t _coordinates_in_image_(
	image_data *in_image, int16_t x, int16_t y
	)
{
	if(x < 0 || x >= in_image->width || y < 0 || y >= in_image->height){ return 0; }
	return 1;
}


int16_t _image_pixel_get_(
	image_data *in_image, int16_t x, int16_t y
	)
{
	if(!_coordinates_in_image_(in_image, x, y)) { return 0; }
	return in_image->data[(in_image->width * y) + x];
}


void _image_pixel_set_(
	image_data *in_image, int16_t x, int16_t y, int16_t value
	)
{
	if(!_coordinates_in_image_(in_image, x, y)) { return; }
	in_image->data[(in_image->width * y) + x] = value;
}


void _image_copy_segment_to_buffer_(
	image_data *in_image, image_data *in_buffer, int16_t x, int16_t y
	)
{
	int16_t m, n;
	for(m = 0; m < in_buffer->width; m++)
	{
		for(n = 0; n < in_buffer->height; n++)
		{
			_image_pixel_set_(in_buffer, m, n, _image_pixel_get_(in_image, x + m, y + n));
		}
	}
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class sample_class:
    def __init__(self, arch, conv, ctypes, dll_handle):

        self._c = ctypes
        self._dll = dll_handle

        class image_data(self._c.Structure):
            _fields_ = [
                ("data", self._c.POINTER(self._c.c_int16)),
                ("width", self._c.c_int16),
                ("height", self._c.c_int16),
            ]

        self.image_data = image_data

        if conv == "cdll":
            func_type = self._c.CFUNCTYPE
        elif conv == "windll":
            func_type = self._c.WINFUNCTYPE
        else:
            raise ValueError("unknown calling convention", conv)
        filter_func_type = func_type(self._c.c_int16, self._c.POINTER(image_data))
        filter_func_type.memsync = [
            {
                "p": [0, "data"],
                "l": ([0, "width"], [0, "height"]),
                "f": "lambda x, y: x * y",
                "t": "c_int16",
            }
        ]

        self.__apply_filter_to_image__ = self._dll.apply_filter_to_image
        self.__apply_filter_to_image__.argtypes = (
            self._c.POINTER(image_data),
            self._c.POINTER(image_data),
            filter_func_type,
        )
        self.__apply_filter_to_image__.memsync = [
            {
                "p": [0, "data"],
                "l": ([0, "width"], [0, "height"]),
                "f": "lambda x, y: x * y",
                "t": "c_int16",
            },
            {
                "p": [1, "data"],
                "l": ([1, "width"], [1, "height"]),
                "f": "lambda x, y: x * y",
                "t": "c_int16",
            },
        ]

        @filter_func_type
        def filter_edge_detection(in_buffer):

            filter_matrix = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]

            width = in_buffer.contents.width
            height = in_buffer.contents.height

            assert width == 3 and height == 3

            in_matrix = self.array_to_matrix(
                self._c.cast(
                    in_buffer.contents.data,
                    self._c.POINTER(self._c.c_int16 * (width * height)),
                ).contents[:],
                width,
                height,
            )

            out_value = 0
            for matrix_line, filter_line in zip(in_matrix, filter_matrix):
                out_value += sum([a * b for a, b in zip(matrix_line, filter_line)])

            return out_value

        self.__filter_edge_detection__ = filter_edge_detection

    def apply_filter_to_image(self, in_image):

        width = len(in_image[0])
        height = len(in_image)

        in_image_ctypes = self.image_data()
        out_image_ctypes = self.image_data()

        in_image_ctypes.width = self._c.c_int16(width)
        in_image_ctypes.height = self._c.c_int16(height)
        in_image_ctypes.data = self._c.cast(
            self._c.pointer(
                (self._c.c_int16 * (width * height))(*self.matrix_to_array(in_image))
            ),
            self._c.POINTER(self._c.c_int16),
        )

        self.__apply_filter_to_image__(
            self._c.pointer(in_image_ctypes),
            self._c.pointer(out_image_ctypes),
            self.__filter_edge_detection__,
        )

        return self.array_to_matrix(
            self._c.cast(
                out_image_ctypes.data,
                self._c.POINTER(self._c.c_int16 * (width * height)),
            ).contents[:],
            width,
            height,
        )

    def array_to_matrix(self, in_array, a_width, a_height):
        return [in_array[(i * a_width) : ((i + 1) * a_width)] for i in range(a_height)]

    def matrix_to_array(self, in_matrix):
        return [item for line_list in in_matrix for item in line_list]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_apply_filter_to_image(arch, conv, ctypes, dll_handle):

    sample = sample_class(arch, conv, ctypes, dll_handle)

    result = sample.apply_filter_to_image(
        [
            [253, 252, 254, 243, 243, 230, 251, 247, 255, 254],
            [252, 254, 239, 144, 253, 247, 220, 252, 235, 255],
            [252, 246, 166, 123, 168, 237, 244, 252, 235, 255],
            [255, 228, 176, 103, 138, 250, 228, 252, 252, 252],
            [219, 217, 146, 152, 146, 170, 250, 253, 246, 243],
            [254, 162, 116, 128, 133, 154, 247, 255, 244, 253],
            [224, 116, 136, 154, 129, 147, 189, 248, 254, 205],
            [192, 105, 117, 138, 148, 101, 111, 248, 248, 239],
            [254, 231, 168, 153, 124, 113, 111, 207, 238, 245],
            [216, 255, 251, 235, 247, 227, 175, 182, 249, 248],
        ]
    )

    assert [
        [-508, -247, -282, -331, -246, -179, -307, -230, -284, -506],
        [-249, -27, -138, 282, -210, -48, 114, -54, 57, -276],
        [-255, -84, 120, 89, 79, -39, -39, -25, 54, -278],
        [-321, -18, -61, 177, 115, -227, 84, -23, -23, -258],
        [-150, -113, 77, -85, 9, 120, -102, -9, 8, -221],
        [-411, 55, 108, 43, 25, 81, -140, -28, 32, -320],
        [-334, 163, -41, -85, 66, -15, -3, -46, -71, -74],
        [-185, 236, 79, 20, -100, 115, 205, -178, -13, -258],
        [-377, -142, 80, 53, 165, 111, 162, -49, -3, -255],
        [-355, -322, -346, -289, -402, -373, -180, -97, -328, -498],
    ] == result
