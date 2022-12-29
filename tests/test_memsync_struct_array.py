# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_memsync_struct_array.py: Tests memsync on an array of structs

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
typedef struct Vector5d {
    int16_t x, y, z, u, w;
} Vector5d;

{{ PREFIX }} Vector5d {{ SUFFIX }} *vector5d_add_array(
    Vector5d *v,
    int16_t len
    );
"""

SOURCE = """
{{ PREFIX }} Vector5d {{ SUFFIX }} *vector5d_add_array(
    Vector5d *v,
    int16_t len
    )
{

    int16_t i;

    Vector5d *v_out = malloc(sizeof(Vector5d));
    v_out->x = 0;
    v_out->y = 0;
    v_out->z = 0;
    v_out->u = 0;
    v_out->w = 0;

    for(i = 0; i < len; i++)
    {
        v_out->x += v[i].x;
        v_out->y += v[i].y;
        v_out->z += v[i].z;
        v_out->u += v[i].u;
        v_out->w += v[i].w;
    }

    return v_out;

}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from typing import Dict, List

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_memsync_struct_array(arch, conv, ctypes, dll_handle):
    """
    Tests memsync on an array of struct objects
    """

    class Vector5d(ctypes.Structure):
        _fields_ = [
            ("x", ctypes.c_int16),
            ("y", ctypes.c_int16),
            ("z", ctypes.c_int16),
            ("u", ctypes.c_int16),
            ("w", ctypes.c_int16),
        ]

    vector5d_add_array_dll = dll_handle.vector5d_add_array
    vector5d_add_array_dll.argtypes = (
        ctypes.POINTER(Vector5d),
        ctypes.c_int16,
    )
    vector5d_add_array_dll.restype = ctypes.POINTER(Vector5d)
    vector5d_add_array_dll.memsync = [
        {"p": [0], "l": [1], "t": Vector5d}
    ]

    def vector5d_add_array(vectors: List[Dict[str, int]]) -> Dict[str, int]:
        """
        User-facing wrapper around DLL function
        """

        length = len(vectors)

        ct_vectors = (Vector5d * length)()
        for idx, vector in enumerate(vectors):
            for name, value in vector.items():
                setattr(ct_vectors[idx], name, value)

        return dict_from_struct(
            vector5d_add_array_dll(
                ctypes.cast(
                    ctypes.pointer(ct_vectors), ctypes.POINTER(Vector5d)
                ),
                length,
            )
        )

    def dict_from_struct(vector: Vector5d) -> Dict[str, int]:
        """
        Helper
        """

        return {name: getattr(vector.contents, name) for name, _ in Vector5d._fields_}

    v = [
        {"x": 5, "y": 7, "z": 2, "u": 4, "w": 6},
        {"x": 1, "y": 9, "z": 8, "u": 3, "w": 2},
    ]
    added = {"x": 6, "y": 16, "z": 10, "u": 7, "w": 8}

    assert added == vector5d_add_array(v)
