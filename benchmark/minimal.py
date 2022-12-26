# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    benchmark/minimal.py: Minimal call, two parameters, no pointers or memsync

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
{{ PREFIX }} int {{ SUFFIX }} add_int(
    int a,
    int b
    );
"""

SOURCE = """
{{ PREFIX }} int {{ SUFFIX }} add_int(
    int a,
    int b
    )
{
    return a + b;
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from tests.lib.benchmark import benchmark

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# BENCHMARK(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def init(ctypes, dll_handle, conv):

    add_int = dll_handle.add_int
    add_int.argtypes = (ctypes.c_int, ctypes.c_int)
    add_int.restype = ctypes.c_int

    return add_int


@benchmark(fn = __file__, initializer = init)
def minimal(ctypes, func):
    """
    The "minimal" benchmark is a simple function call with
    two ``c_int`` parameters and a single ``c_int`` return value.
    The DLL function simply adds the two numbers and returns the result.
    """

    x, y = 3, 4
    z = func(x, y)
    assert z == 7
