# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/param.py: Providing test parameters and helpers

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
# CONST / CONFIG
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

MAX_EXAMPLES = 300

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def get_int_limits(bits, sign=True):
    assert isinstance(bits, int)
    assert bits in (8, 16, 32, 64)
    assert isinstance(sign, bool)
    if sign:
        return {"min_value": -1 * 2 ** (bits - 1), "max_value": 2 ** (bits - 1) - 1}
    else:
        return {"min_value": 0, "max_value": 2 ** bits - 1}


def force_int_overflow(value, bits, sign):
    assert isinstance(value, int)
    assert isinstance(bits, int)
    assert bits in (8, 16, 32, 64)
    assert isinstance(sign, bool)
    int_limits = get_int_limits(bits, sign)
    while value > int_limits["max_value"]:
        value -= 2 ** bits
    while value < int_limits["min_value"]:
        value += 2 ** bits
    return value
