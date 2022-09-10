#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	examples/test_callback.py: Demonstrates callback routines as arguments

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

from sys import platform

if any([platform.startswith(os_name) for os_name in ["linux", "darwin", "freebsd"]]):

    f = open(".zugbruecke.json", "w")
    f.write('{"log_level": 10}')
    f.close()

    import zugbruecke.ctypes as ctypes

elif platform.startswith("win"):

    import ctypes

else:

    raise  # TODO unsupported platform


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# RUN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":

    DATA = [1, 6, 8, 4, 9, 7, 4, 2, 5, 2]

    conveyor_belt = ctypes.WINFUNCTYPE(ctypes.c_int16, ctypes.c_int16)

    @conveyor_belt
    def get_data(index):
        print((index, DATA[index]))
        return DATA[index]

    dll = ctypes.windll.LoadLibrary("demo_dll.dll")
    sum_elements_from_callback = dll.sum_elements_from_callback
    sum_elements_from_callback.argtypes = (ctypes.c_int16, conveyor_belt)
    sum_elements_from_callback.restype = ctypes.c_int16

    test_sum = sum_elements_from_callback(len(DATA), get_data)
    print(("sum", 48, test_sum))

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    class conveyor_belt_data(ctypes.Structure):
        _fields_ = [("len", ctypes.c_int16), ("get_data", conveyor_belt)]

    sum_elements_from_callback_in_struct = dll.sum_elements_from_callback_in_struct
    sum_elements_from_callback_in_struct.argtypes = (
        ctypes.POINTER(conveyor_belt_data),
    )
    sum_elements_from_callback_in_struct.restype = ctypes.c_int16

    in_struct = conveyor_belt_data(len(DATA), get_data)

    test_struct_sum = sum_elements_from_callback_in_struct(in_struct)
    print(("sum", 48, test_struct_sum))
