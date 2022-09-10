# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_vector3d_add.py: Tests pointer to struct type return value

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
typedef struct vector3d {
	int16_t x, y, z;
} vector3d;

{{ PREFIX }} vector3d {{ SUFFIX }} *vector3d_add(
	vector3d *v1,
	vector3d *v2
	);

{{ PREFIX }} vector3d {{ SUFFIX }} *vector3d_add_array(
	vector3d *v,
	int16_t len
	);
"""

SOURCE = """
{{ PREFIX }} vector3d {{ SUFFIX }} *vector3d_add(
	vector3d *v1,
	vector3d *v2
	)
{

	vector3d *v3 = malloc(sizeof(vector3d));

	v3->x = v1->x + v2->x;
	v3->y = v1->y + v2->y;
	v3->z = v1->z + v2->z;

	return v3;

}

{{ PREFIX }} vector3d {{ SUFFIX }} *vector3d_add_array(
	vector3d *v,
	int16_t len
	)
{

	int16_t i;

	vector3d *v_out = malloc(sizeof(vector3d));
	v_out->x = 0;
	v_out->y = 0;
	v_out->z = 0;

	for(i = 0; i < len; i++)
	{
		v_out->x += v[i].x;
		v_out->y += v[i].y;
		v_out->z += v[i].z;
	}

	return v_out;

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


class sample_class_a:
    def __init__(self, ctypes, dll_handle):
        class vector3d(ctypes.Structure):
            _fields_ = [
                ("x", ctypes.c_int16),
                ("y", ctypes.c_int16),
                ("z", ctypes.c_int16),
            ]

        self._vector3d = vector3d

        self._vector3d_add = dll_handle.vector3d_add
        self._vector3d_add.argtypes = (
            ctypes.POINTER(self._vector3d),
            ctypes.POINTER(self._vector3d),
        )
        self._vector3d_add.restype = ctypes.POINTER(self._vector3d)

    def vector3d_add(self, v1, v2):
        def struct_from_dict(in_dict):
            return self._vector3d(*tuple(in_dict[key] for key in ["x", "y", "z"]))

        def dict_from_struct(in_struct):
            return {key: getattr(in_struct.contents, key) for key in ["x", "y", "z"]}

        return dict_from_struct(
            self._vector3d_add(struct_from_dict(v1), struct_from_dict(v2))
        )


class sample_class_b:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes

        class vector3d(self._c.Structure):
            _fields_ = [
                ("x", self._c.c_int16),
                ("y", self._c.c_int16),
                ("z", self._c.c_int16),
            ]

        self._vector3d = vector3d

        self._vector3d_add_array = dll_handle.vector3d_add_array
        self._vector3d_add_array.argtypes = (
            self._c.POINTER(self._vector3d),
            self._c.c_int16,
        )
        self._vector3d_add_array.restype = self._c.POINTER(self._vector3d)
        self._vector3d_add_array.memsync = [
            {"p": [0], "l": [1], "t": "vector3d@{ID:d}".format(ID=id(vector3d))}
        ]

    def vector3d_add_array(self, v):

        length = len(v)

        def dict_from_struct(in_struct):
            return {key: getattr(in_struct.contents, key) for key in ["x", "y", "z"]}

        v_ctypes = (self._vector3d * length)()
        for i in range(length):
            for key in v[i].keys():
                setattr(v_ctypes[i], key, v[i][key])

        return dict_from_struct(
            self._vector3d_add_array(
                self._c.cast(
                    self._c.pointer(v_ctypes), self._c.POINTER(self._vector3d)
                ),
                length,
            )
        )


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_vector3d_add(arch, conv, ctypes, dll_handle):

    v1 = {"x": 5, "y": 7, "z": 2}
    v2 = {"x": 1, "y": 9, "z": 8}
    added = {"x": 6, "y": 16, "z": 10}

    sample = sample_class_a(ctypes, dll_handle)

    assert added == sample.vector3d_add(v1, v2)


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_vector3d_add_array(arch, conv, ctypes, dll_handle):

    v = [{"x": 5, "y": 7, "z": 2}, {"x": 1, "y": 9, "z": 8}]
    added = {"x": 6, "y": 16, "z": 10}

    sample = sample_class_b(ctypes, dll_handle)

    assert added == sample.vector3d_add_array(v)
