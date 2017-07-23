#!/usr/bin/env wine-python
# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/_server_.py: Started with Python on Wine, executing DLL calls

	Required to run on platform / side: [WINE]

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

import argparse

from core.session_server import session_server_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# INIT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	# Parse arguments comming from unix side
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--id', type = str, nargs = 1
		)
	parser.add_argument(
		'--port_socket_ctypes', type = int, nargs = 1
		)
	parser.add_argument(
		'--port_socket_log_main', type = int, nargs = 1
		)
	parser.add_argument(
		'--log_level', type = int, nargs = 1
		)
	parser.add_argument(
		'--logwrite', type = int, nargs = 1
		)
	args = parser.parse_args()

	# Generate parameter dict
	parameter = {
		'id': args.id[0],
		'platform': 'WINE',
		'stdout': False,
		'stderr': False,
		'logwrite': bool(args.logwrite[0]),
		'remote_log': True,
		'log_level': args.log_level[0],
		'log_server': False,
		'port_socket_ctypes': args.port_socket_ctypes[0],
		'port_socket_log_main': args.port_socket_log_main[0]
		}

	# Fire up wine server session with parsed parameters
	session = session_server_class(parameter['id'], parameter)
