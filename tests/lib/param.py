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
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from typing import Dict

from typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST / CONFIG
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

MAX_EXAMPLES = 300

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
def get_int_limits(bits: int, sign: bool = True) -> Dict[str, int]:
    """
    computes upper and lower limits of integers of a given number of bits

    Args:
        - bits: Number of bits
        - sign: Indicate signed integer
    Returns
        Dict of min and max values
    """

    assert bits in (8, 16, 32, 64)

    if sign:
        return {"min_value": -1 * 2 ** (bits - 1), "max_value": 2 ** (bits - 1) - 1}
    return {"min_value": 0, "max_value": 2 ** bits - 1}


@typechecked
def force_int_overflow(value: int, bits: int, sign: bool) -> int:
    """
    Emulate C-like integer overflow in Python

    Args:
        - value: Cut off overflow bits from this integer
        - bits: Emulate an integer of this number of bits
        - sign: Indicate the emulation of a signed integer
    """

    assert bits in (8, 16, 32, 64)

    int_limits = get_int_limits(bits, sign)
    while value > int_limits["max_value"]:
        value -= 2 ** bits
    while value < int_limits["min_value"]:
        value += 2 ** bits
    return value
