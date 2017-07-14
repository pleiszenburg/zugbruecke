# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/lib.py: General purpose routines

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

import hashlib
import os
import random
import socket


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LIBRARY ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_free_port():

	s = socket.socket()
	s.bind(('', 0))
	port = s.getsockname()[1]
	s.close()

	return port


def get_hash_of_string(str_in):

	return hashlib.sha256(str_in.encode('utf-8')).hexdigest()


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


def reduce_dict(input_dict):

	output_dict = {}

	# Keep everything, which is not private (does not start with '_')
	for key in input_dict.keys():
		if not key.startswith('_'):
			output_dict[key] = input_dict[key]

	return output_dict
