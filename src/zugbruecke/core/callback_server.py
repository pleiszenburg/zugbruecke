# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/callback_server.py: Classes for managing callback routines

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017-2018 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

from pprint import pformat as pf
import traceback


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CALLBACK SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class callback_translator_server_class:


	def __init__(self, parent_routine, routine_name, routine_handler, argtypes_d, restype_d):

		# Store my own name
		self.name = routine_name

		# Store handler
		self.handler = routine_handler

		# Store handle on parent routine
		self.parent_routine = parent_routine

		# Get handle on log
		self.log = self.parent_routine.log

		# Store definition of argument types
		self.argtypes_d = argtypes_d

		# Store definition of return value type
		self.restype_d = restype_d

		# Store handlers on packing/unpacking routines
		self.arg_list_pack = self.parent_routine.arg_list_pack
		self.arg_list_sync = self.parent_routine.arg_list_sync
		self.arg_list_unpack = self.parent_routine.arg_list_unpack
		self.return_msg_unpack = self.parent_routine.return_msg_unpack


	def __call__(self, *args):

		# Log status
		self.log.out('[callback-server] Trying to call callback routine "%s" ...' % self.name)

		# Log status
		self.log.out('[callback-server] ... parameters are "%r". Packing and pushing to client ...' % (args,))

		# Pack arguments and call RPC callback function (packed arguments are shipped to Unix side)
		return_dict = self.handler(self.arg_list_pack(args, self.argtypes_d))

		# Log status
		self.log.out('[callback-server] ... received feedback from client, unpacking ...')

		# Unpack return dict (for pointers and structs)
		self.arg_list_sync(
			args,
			self.arg_list_unpack(return_dict['args'], self.argtypes_d),
			self.argtypes_d
			)

		# Unpack return value
		return_value = self.return_msg_unpack(return_dict['return_value'], self.restype_d)

		# Log status
		self.log.out('[callback-server] ... unpacked, return.')

		# Return data directly to DLL routine
		return return_value
