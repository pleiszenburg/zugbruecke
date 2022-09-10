# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/path.py: Coverts paths fron Unix to Wine format and vv

    Required to run on platform / side: [WINE]

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

import ctypes
from ctypes import wintypes

from .errors import WineError
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PATH CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class PathStyles:
    """
    Coverts paths fron Unix to Wine format and vice versa
    """

    def __init__(self):

        self._unix_to_wine = ctypes.cdll.kernel32.wine_get_dos_file_name
        self._unix_to_wine.argtypes = (wintypes.LPCSTR,)
        self._unix_to_wine.restype = wintypes.LPCWSTR

        self._wine_to_unix = ctypes.cdll.kernel32.wine_get_unix_file_name
        self._wine_to_unix.argtypes = (wintypes.LPCWSTR,)
        self._wine_to_unix.restype = wintypes.LPCSTR

    def unix_to_wine(self, in_path: str) -> str:
        """
        In: Unix path
        Out: Wine path
        """

        if not isinstance(in_path, str):
            raise TypeError("in_path must by of type str")

        out_path = self._unix_to_wine(
            ctypes.cast(
                ctypes.create_string_buffer(in_path.encode("utf-8")), wintypes.LPCSTR
            )
        )

        if out_path is None:
            raise WineError()

        return out_path

    def wine_to_unix(self, in_path: str) -> str:
        """
        In: Wine path
        Out: Unix path
        """

        if not isinstance(in_path, str):
            raise TypeError("in_path must by of type str")

        out_path = self._wine_to_unix(
            ctypes.cast(ctypes.create_unicode_buffer(in_path), wintypes.LPCWSTR)
        )

        if out_path is None:
            raise WineError()

        return out_path.decode("utf-8")
