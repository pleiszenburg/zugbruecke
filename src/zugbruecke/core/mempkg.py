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
from .typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Mempkg(MempkgABC):
    """
    Represents a block of memory to be kept in sync
    """

    def __init__(
        self,
        data: bytes,  # serialized data, '' if NULL pointer
        local_addr: Optional[int],  # local pointer address as integer
        remote_addr: Optional[int],  # remote pointer has not been initialized
        wchar: Optional[int],  # local length of Unicode wchar if required
        ptr: Optional[Any] = None,  # original ctypes pointer to avoid garbage collection on client
    ):

        self._data = data
        self._local_addr = local_addr
        self._remote_addr = remote_addr
        self._wchar = wchar
        self._ptr = ptr

    def __repr__(self) -> str:

        return f'<Mempkg len={len(self):d} local_addr={self._local_addr:x} remote_addr={self._remote_addr:x}>'

    def __len__(self) -> int:

        return len(self._data)

    @property
    def data(self) -> bytes:

        return self._data

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

        tmp = bytearray(len(mempkg["data"]) * new_len // old_len)

        for index in range(old_len if new_len > old_len else new_len):
            tmp[index::new_len] = mempkg["data"][index::old_len]

        mempkg["data"] = bytes(tmp)
        mempkg["wchar"] = new_len

    def make_pointer(self) -> Any:
        """
        Generate pointer around data
        """

        return ctypes.cast(
            ctypes.pointer((ctypes.c_ubyte * len(self)).from_buffer_copy(self._data)),
            ctypes.c_void_p,
        )

    def overwrite(self):
        """
        Write data to local address
        """

        ctypes.memmove(
            ctypes.c_void_p(self._local_addr),
            ctypes.pointer((ctypes.c_ubyte * len(self)).from_buffer_copy(self._data)),
            len(self),
        )

    def update(self, other: MempkgABC):
        """
        Update package from other package

        Args:
            - other: Other memory package
        """

        self._data = other.data
        self._local_addr = other.local_addr
        self._remote_addr = other.remote_addr
        self._wchar = other.wchar

    def update_data(self):
        """
        Update data from local address
        """

        self._data = bytes(
            ctypes.cast(
                ctypes.c_void_p(self._local_addr),
                ctypes.POINTER(ctypes.c_ubyte * len(self)),
            ).contents
        )

    def as_packed(self) -> Dict:
        """
        Pack for shipping
        """

        return {
            'data': self._data,
            'local_addr': self._local_addr,
            'remote_addr': self._remote_addr,
            'wchar': self._wchar,
        }

    @classmethod
    def from_packed(cls, packed: Dict):
        """
        Unpack from shipping, fix wchar size, swap addresses
        """

        packed.update({
            'local_addr': packed['remote_addr'],  # swap
            'remote_addr': packed['local_addr'],  # swap
        })

        if packed.get('wchar', None) is not None:
            cls._adjust_wchar_length(packed)

        return cls(**packed)

    @classmethod
    def from_pointer(cls, ptr: Any, length: int, wchar: Optional[int]):
        """
        Generate package from ctypes pointer

        Args:
            - ptr: ctypes pointer
            - length: number of bytes
            - wchar: length of wchar on platform
        """

        return cls(
            data = bytes(
                ctypes.cast(
                    ptr, ctypes.POINTER(ctypes.c_ubyte * length)
                ).contents
            ),
            local_addr = ctypes.cast(ptr, ctypes.c_void_p).value,
            remote_addr = None,
            wchar = wchar,
            ptr = ptr,
        )
