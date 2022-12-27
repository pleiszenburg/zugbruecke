# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_struct_pointer.py: Tests pointer to struct of fixed size

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
typedef struct Vector4d {
    int16_t x, y, z, u;
} Vector4d;

{{ PREFIX }} Vector4d {{ SUFFIX }} *vector4d_add(
    Vector4d *v1,
    Vector4d *v2
    );
"""

SOURCE = """
{{ PREFIX }} Vector4d {{ SUFFIX }} *vector4d_add(
    Vector4d *v1,
    Vector4d *v2
    )
{

    Vector4d *v3 = malloc(sizeof(Vector4d));

    v3->x = v1->x + v2->x;
    v3->y = v1->y + v2->y;
    v3->z = v1->z + v2->z;
    v3->u = v1->u + v2->u;

    return v3;

}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from typing import Dict

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_struct_pointer(arch, conv, ctypes, dll_handle):
    """
    Testing pointer to individual struct object of fixed size (no memsync required)
    """

    class Vector4d(ctypes.Structure):
        _fields_ = [
            ("x", ctypes.c_int16),
            ("y", ctypes.c_int16),
            ("z", ctypes.c_int16),
            ("u", ctypes.c_int16),
        ]

    vector4d_add_dll = dll_handle.vector4d_add
    vector4d_add_dll.argtypes = (
        ctypes.POINTER(Vector4d),
        ctypes.POINTER(Vector4d),
    )
    vector4d_add_dll.restype = ctypes.POINTER(Vector4d)

    def vector4d_add(v1: Dict[str, int], v2: Dict[str, int]) -> Dict[str, int]:
        """
        User-facing wrapper around DLL function
        """

        return dict_from_struct(
            vector4d_add_dll(struct_from_dict(v1), struct_from_dict(v2))
        )

    def struct_from_dict(vector: Dict[str, int]):
        """
        Helper
        """

        return Vector4d(**vector)

    def dict_from_struct(vector: Vector4d):
        """
        Helper
        """

        return {name: getattr(vector.contents, name) for name, _ in Vector4d._fields_}

    v1 = {"x": 5, "y": 7, "z": 2, "u": 4}
    v2 = {"x": 1, "y": 9, "z": 8, "u": 3}
    added = {"x": 6, "y": 16, "z": 10, "u": 7}

    assert added == vector4d_add(v1, v2)
