# -*- coding: utf-8 -*-

"""
pycrosscall - Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD
Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

	pycrosscall/lib.py: General purpose routines.

Licensed under the LGPL 2.1. For details, see:
- https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
- https://github.com/s-m-e/pycrosscall/blob/master/LICENSE
"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import random


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LIBRARY ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_location_of_file(filename = ''):

	if filename == '':
		filename = __file__

	return os.path.split(os.path.realpath(filename))[0]


def get_randhashstr(dig):

	# Return hash string with dig digits
	return (('%0' + str(dig) + 'x') % random.randrange(16**dig))


def generate_session_id():

	# A session id by default is an 8 digit hash string
	return get_randhashstr(8)
