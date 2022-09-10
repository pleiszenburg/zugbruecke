#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	examples/test_zugbruecke.py: Demonstrates ctypes examples from Cookbook R3

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

# import sys
# import os
# import time
from sys import argv, platform
import timeit

# Timing mode?
TIMING_RUN = False
try:
    if "time" in argv:
        TIMING_RUN = True
except:
    pass

if any([platform.startswith(os_name) for os_name in ["linux", "darwin", "freebsd"]]):

    f = open(".zugbruecke.json", "w")
    if TIMING_RUN:
        f.write("{}")
    else:
        f.write('{"log_level": 10}')
    f.close()
    import zugbruecke.ctypes as ctypes

elif platform.startswith("win"):

    import ctypes

else:

    raise  # TODO unsupported platform


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Define a special type for the 'double *' argument
class DoubleArrayType:
    def from_param(self, param):

        typename = type(param).__name__
        if hasattr(self, "from_" + typename):
            return getattr(self, "from_" + typename)(param)
        elif isinstance(param, ctypes.Array):
            return param
        else:
            raise TypeError("Can't convert %s" % typename)

    # Cast from array.array objects
    def from_array(self, param):

        if param.typecode != "d":
            raise TypeError("must be an array of doubles")
        ptr, _ = param.buffer_info()
        return ctypes.cast(ptr, ctypes.POINTER(ctypes.c_double))

    # Cast from lists/tuples
    def from_list(self, param):

        val = ((ctypes.c_double) * len(param))(*param)
        return val

    from_tuple = from_list

    # Cast from a numpy array
    def from_ndarray(self, param):

        return param.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


# struct Point { }
class Point(ctypes.Structure):

    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]


class sample_class:
    def __init__(self):

        self.__dll__ = ctypes.windll.LoadLibrary("demo_dll.dll")

        # int gcd(int, int)
        self.gcd = self.__dll__.cookbook_gcd
        self.gcd.argtypes = (ctypes.c_int, ctypes.c_int)
        self.gcd.restype = ctypes.c_int

        # int in_mandel(double, double, int)
        self.in_mandel = self.__dll__.cookbook_in_mandel
        self.in_mandel.argtypes = (ctypes.c_double, ctypes.c_double, ctypes.c_int)
        self.in_mandel.restype = ctypes.c_int

        # int divide(int, int, int *)
        self.__divide__ = self.__dll__.cookbook_divide
        self.__divide__.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
        )
        self.__divide__.restype = ctypes.c_int

        # void avg(double *, int n)
        DoubleArray = DoubleArrayType()
        self.__avg__ = self.__dll__.cookbook_avg
        self.__avg__.memsync = [  # Regular ctypes on Windows should ignore this statement
            {
                "p": [0],  # "path" to argument containing the pointer
                "l": [1],  # "path" to argument containing the length
                "t": "c_double",  # type of argument (optional, default char/byte): sizeof(type) * length == bytes
                "_c": DoubleArray,  # custom datatype
            }
        ]
        self.__avg__.argtypes = (DoubleArray, ctypes.c_int)
        self.__avg__.restype = ctypes.c_double

        # void bubblesort(float *, int n)
        self.__bubblesort__ = self.__dll__.bubblesort
        self.__bubblesort__.memsync = [  # Regular ctypes on Windows should ignore this statement
            {
                "p": [0],  # "path" to argument containing the pointer
                "l": [1],  # "path" to argument containing the length
                "t": "c_float",  # type of argument (optional, default char/byte): sizeof(type) * length == bytes
            }
        ]
        self.__bubblesort__.argtypes = (ctypes.POINTER(ctypes.c_float), ctypes.c_int)

        # double distance(Point *, Point *)
        self.distance = self.__dll__.cookbook_distance
        self.distance.argtypes = (ctypes.POINTER(Point), ctypes.POINTER(Point))
        self.distance.restype = ctypes.c_double

        # void mix_rgb_colors(int8_t [3], int8_t [3], int8_t *)
        self.__mix_rgb_colors__ = self.__dll__.mix_rgb_colors
        self.__mix_rgb_colors__.argtypes = (
            ctypes.c_ubyte * 3,
            ctypes.c_ubyte * 3,
            ctypes.POINTER(ctypes.c_ubyte * 3),
        )

        # void gauss_elimination(float [3][4] *)
        self.__gauss_elimination__ = self.__dll__.gauss_elimination
        self.__gauss_elimination__.argtypes = (
            ctypes.POINTER(ctypes.c_float * 4 * 3),
            ctypes.POINTER(ctypes.c_float * 3),
        )

    def avg(self, values):

        return self.__avg__(values, len(values))

    def bubblesort(self, values):

        ctypes_float_values = ((ctypes.c_float) * len(values))(*values)
        ctypes_float_pointer_firstelement = ctypes.cast(
            ctypes.pointer(ctypes_float_values), ctypes.POINTER(ctypes.c_float)
        )
        self.__bubblesort__(ctypes_float_pointer_firstelement, len(values))
        values[:] = ctypes_float_values[:]

    def mix_rgb_colors(self, color_a, color_b):

        color_type = ctypes.c_ubyte * 3
        ctypes_color_a = color_type(*tuple(color_a))
        ctypes_color_b = color_type(*tuple(color_b))
        mixed_color = color_type()
        self.__mix_rgb_colors__(
            ctypes_color_a, ctypes_color_b, ctypes.pointer(mixed_color)
        )
        return mixed_color[:]

    def divide(self, x, y):

        rem = ctypes.c_int()
        quot = self.__divide__(x, y, rem)
        return quot, rem.value

    def gauss_elimination(self, A):

        N = 3
        if len(A) != N or len(A[0]) != N + 1:
            raise  # TODO

        x = [0 for eq in range(N)]
        _A = (ctypes.c_float * (N + 1) * N)(*(tuple(eq) for eq in A))
        _x = (ctypes.c_float * N)(*tuple(x))
        self.__gauss_elimination__(ctypes.pointer(_A), ctypes.pointer(_x))
        for index, eq in enumerate(A):
            eq[:] = _A[index][:]
        x[:] = _x[:]

        return x


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# RUN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":

    sample = sample_class()

    def time_ROUTINE(routine_name):

        t = timeit.Timer(
            "time_%s()" % routine_name,
            setup="from __main__ import time_%s" % routine_name,
        )
        print("[TIME %s] %f" % (routine_name, t.timeit(number=100000)))

    print(7, sample.gcd(35, 42))

    def time_gdc():
        returnvalue = sample.gcd(35, 42)

    if TIMING_RUN:
        time_ROUTINE("gdc")

    print(1, sample.in_mandel(0, 0, 500))

    def time_in_mandel_1():
        returnvalue = sample.in_mandel(0, 0, 500)

    if TIMING_RUN:
        time_ROUTINE("in_mandel_1")

    print(0, sample.in_mandel(2.0, 1.0, 500))

    def time_in_mandel_2():
        returnvalue = sample.in_mandel(2.0, 1.0, 500)

    if TIMING_RUN:
        time_ROUTINE("in_mandel_2")

    print((5, 2), sample.divide(42, 8))

    def time_divide():
        returnvalue = sample.divide(42, 8)

    if TIMING_RUN:
        time_ROUTINE("divide")

    print(4.0, sample.avg([1, 2, 9]))

    def time_avg():
        returnvalue = sample.avg([1, 2, 6])

    if TIMING_RUN:
        time_ROUTINE("avg")

    test_vector = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
    sample.bubblesort(test_vector)
    test_vector = [round(element, 2) for element in test_vector]
    print([2.05, 3.72, 4.39, 4.75, 5.74, 6.28, 6.47, 8.6, 9.09, 9.34])
    print(test_vector)

    def time_bubblesort():
        sample.bubblesort([5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75])

    if TIMING_RUN:
        time_ROUTINE("bubblesort")

    p1 = Point(1, 2)
    p2 = Point(4, 5)
    print(4.242640687119285, sample.distance(p1, p2))

    def time_distance():
        p1 = Point(1, 2)
        p2 = Point(4, 5)
        returnvalue = sample.distance(p1, p2)

    if TIMING_RUN:
        time_ROUTINE("distance")

    print([45, 35, 30], sample.mix_rgb_colors([10, 20, 40], [80, 50, 20]))

    def time_mix_rgb_colors():
        returnvalue = sample.mix_rgb_colors([10, 20, 40], [80, 50, 30])

    if TIMING_RUN:
        time_ROUTINE("mix_rgb_colors")

    eq_sys = [[1, 2, 3, 2], [1, 1, 1, 2], [3, 3, 1, 0]]
    print([5.0, -6.0, 3.0], sample.gauss_elimination(eq_sys))
    print(
        [[1.0, 2.0, 3.0, 2.0], [0.0, -1.0, -2.0, 0.0], [0.0, 0.0, -2.0, -6.0]], eq_sys
    )
    # def time_gauss_elimination():
    # 	returnvalue = sample.gauss_elimination([10, 20, 40], [80, 50, 30])
    # if TIMING_RUN:
    # 	time_ROUTINE('gauss_elimination')
