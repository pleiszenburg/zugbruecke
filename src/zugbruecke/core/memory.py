# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/memory.py: Handles memory transfers between both sides

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

from typing import Any
import ctypes

from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def is_null_pointer(ctypes_pointer):

    try:
        return ctypes.cast(ctypes_pointer, ctypes.c_void_p).value is None
    except ctypes.ArgumentError:  # catch non-pointer arguments
        return False


@typechecked
def strip_pointer(item: Any) -> Any:
    """
    Args:
        - item: ctypes pointer object
    Returns:
        ctypes object, extracted from pointer
    """

    # Handle pointer object
    if hasattr(item, "contents"):
        return item.contents

    # Handle reference (byref) 'light pointer'
    if hasattr(item, "_obj"):
        return item._obj

    # Object was likely not provided as a pointer
    return item


@typechecked
def strip_simplecdata(item: Any) -> Any:
    """
    Args:
        - item: potentially some ctypes SimpleCData object
    Returns:
        Raw value, extracted from ctypes SimpleCData object
    """

    return getattr(item, "value", item)
