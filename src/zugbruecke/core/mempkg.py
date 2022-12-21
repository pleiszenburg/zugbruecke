# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/mempkg.py: Memory (data) package

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

import ctypes
from typing import Any, Dict, Optional

from .abc import MempkgABC
from .memory import (
    generate_pointer_from_bytes,
    overwrite_pointer_with_bytes,
    serialize_pointer_into_bytes,
)
from .typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Mempkg(MempkgABC):
    """
    Represent the definition of a block of memory to be kept in sync
    """

    def __init__(
        self,
        data: bytes,  # serialized data, '' if NULL pointer
        length: int,  # length of serialized data
        local_addr: Optional[int],  # local pointer address as integer
        remote_addr: Optional[int],  # remote pointer has not been initialized
        wchar: Optional[int],  # local length of Unicode wchar if required
    ):

        self._data = data
        self._length = length
        self._local_addr = local_addr
        self._remote_addr = remote_addr
        self._wchar = wchar

    def __repr__(self) -> str:

        return f'<Mempkg length={self._length:d} local_addr={self._local_addr:x} remote_addr={self._remote_addr:x}>'

    @property
    def data(self) -> bytes:

        return self._data

    @property
    def length(self) -> int:

        return self._length

    @property
    def local_addr(self) -> Optional[int]:

        return self._local_addr

    @local_addr.setter
    def local_addr(self, value: Optional[int]):

        self._local_addr = value

    @property
    def remote_addr(self) -> Optional[int]:

        return self._remote_addr

    @property
    def wchar(self) -> Optional[int]:

        return self._wchar

    @staticmethod
    def _adjust_wchar_length(mempkg: Dict):
        """
        Adjust number of bytes per unicode character

        Args:
            - mempkg: Packed memory package for/from shipping
        Returns:
            Nothing
        """

        old_len = mempkg["wchar"]
        new_len = ctypes.sizeof(ctypes.c_wchar)

        if old_len == new_len:
            return

        tmp = bytearray(mempkg["length"] * new_len // old_len)

        for index in range(old_len if new_len > old_len else new_len):
            tmp[index::new_len] = mempkg["data"][index::old_len]

        mempkg["data"] = bytes(tmp)
        mempkg["length"] = len(mempkg["data"])
        mempkg["wchar"] = new_len

    def make_pointer(self) -> Any:
        """
        Generate pointer around data
        """

        return generate_pointer_from_bytes(self._data)

    def overwrite(self):
        """
        Write data to local address
        """

        overwrite_pointer_with_bytes(ctypes.c_void_p(self._local_addr), self._data)

    def update(self, other: MempkgABC):
        """
        Update package from other package

        Args:
            - other: Other memory package
        """

        self._data = other.data
        self._length = other.length
        self._local_addr = other.local_addr
        self._remote_addr = other.remote_addr
        self._wchar = other.wchar

    def update_data(self):
        """
        Update data from local address
        """

        self._data = serialize_pointer_into_bytes(
            ctypes.c_void_p(self._local_addr), self._length
        )

    def as_packed(self) -> Dict:

        return {
            'data': self._data,
            'length': self._length,
            'local_addr': self._local_addr,
            'remote_addr': self._remote_addr,
            'wchar': self._wchar,
        }

    @classmethod
    def from_packed(cls, packed: Dict):

        packed.update({
            'local_addr': packed['remote_addr'],  # swap
            'remote_addr': packed['local_addr'],  # swap
        })

        if packed.get('wchar', None) is not None:
            cls._adjust_wchar_length(packed)

        return cls(**packed)
