# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/callback_server.py: Classes for managing callback routines

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

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


	def __init__(self, data, routine_name, routine_handler, argtypes_d, restype_d, memsync_d):

		# Store my own name
		self.name = routine_name

		# Store handler
		self.handler = routine_handler

		# Store handle on data
		self.data = data

		# Get handle on log
		self.log = self.data.log

		# Store definition of argument types
		self.argtypes_d = argtypes_d

		# Store definition of return value type
		self.restype_d = restype_d

		# Store memsync definition
		self.memsync_d = memsync_d


	def __call__(self, *args):

		# Log status
		self.log.out('[callback-server] Trying to call callback routine "%s" ...' % self.name)

		# Log status
		self.log.out('[callback-server] ... parameters are "%r". Packing and pushing to client ...' % (args,))

		try:

			# Handle memory
			mem_package_list = self.data.client_pack_memory_list(args, self.memsync_d)

		except Exception as e:

			# Log status
			self.log.out('[callback-server] ... memory packing failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

			raise e

		try:

			# Pack arguments and call RPC callback function (packed arguments are shipped to Unix side)
			return_dict = self.handler(self.data.arg_list_pack(args, self.argtypes_d), mem_package_list)

		except Exception as e:

			# Log status
			self.log.out('[callback-server] ... call failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

			raise e

		try:

			# Log status
			self.log.out('[callback-server] ... received feedback from client, unpacking ...')

			# Unpack return dict (for pointers and structs)
			self.data.arg_list_sync(
				args,
				self.data.arg_list_unpack(return_dict['args'], self.argtypes_d),
				self.argtypes_d
				)

			# Unpack return value
			return_value = self.data.return_msg_unpack(return_dict['return_value'], self.restype_d)

			# Unpack memory (call may have failed partially only)
			self.data.client_unpack_memory_list(args, return_value, return_dict['memory'], self.memsync_d)

		except Exception as e:

			# Log status
			self.log.out('[callback-server] ... unpacking failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

			raise e

		# Raise the original error if call was not a success
		if not return_dict['success']:
			self.log.out('[callback-server] ... call raised an error.')
			raise return_dict['exception']

		# Log status
		self.log.out('[callback-server] ... unpacked, return.')

		# Return data directly to DLL routine
		return return_value
