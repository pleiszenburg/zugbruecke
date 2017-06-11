# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	pycrosscall/config.py: Handles the modules configuration

	Required to run on platform / side: [UNIX]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/s-m-e/pycrosscall/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import json


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_module_config():

	return __join_config_by_priority__(__locate_and_read_config_files__())


def __join_config_by_priority__(config_dict_list):

	# Gather all the keys ...
	key_set = set()
	for config_dict in config_dict_list:
		key_set.union(set(list(config_dict.keys())))

	# New parameter dict
	parameter_dict = {}

	# Go through list, from low priority to high
	for config_dict in reversed(config_dict_list):

		# Go through keys
		for key in key_set:

			# Change config is needed
			if key in config_dict.keys():
				parameter_dict[key] = config_dict[key]

	return parameter_dict


def __locate_and_read_config_files__():

	# List of config files' contents by priority
	config_dict_list = []

	# Look for config in the usual spots
	for file_location in [
		os.curdir,
		os.environ.get('PYCROSSCALL'),
		os.path.join(os.path.expanduser('~'), '.pycrosscall'),
		'/etc/pycrosscall'
		]:

		# Compile path
		try_path = os.path.join(file_location, 'conf.json')

		# Is this a file?
		if os.path.isfile(try_path):

			# Read file
			f = open(try_path, 'r'):
			cnt = f.read()
			f.close()

			# Try to parse it
			try:
				cnt_json = json.loads(cnt)
				config_dict_list.append(cnt_json)
			except:
				pass # TODO produce an error

	return config_dict_list
