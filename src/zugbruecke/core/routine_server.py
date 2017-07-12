# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/routine_server.py: Classes for managing routines in DLLs

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

import ctypes
from pprint import pformat as pf
import traceback

from .arg_definition import arg_definition_class
from .arg_memory import arg_memory_class
from .const import (
	FLAG_POINTER,
	GROUP_VOID,
	GROUP_FUNDAMENTAL,
	GROUP_STRUCT
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class routine_server_class(
	arg_definition_class,
	arg_memory_class
	):


	def __init__(self, parent_dll, routine_name):

		# Store handle on parent dll
		self.dll = parent_dll

		# Store pointer to zugbruecke session
		self.session = self.dll.session

		# Get handle on log
		self.log = self.dll.log

		# Store my own name
		self.name = routine_name

		# Log status
		self.log.out('[routine-server] Attaching to routine "%s" in DLL file "%s" ...' % (self.name, self.dll.name))

		try:

			# Get handler on routine in dll
			self.handler = getattr(
				self.dll.handler, routine_name
				)

			# Log status
			self.log.out('[routine-server] ... done.')

		except:

			# Log status
			self.log.out('[routine-server] ... failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

			raise # TODO


	def call_routine(self, arg_message_list, arg_memory_list):
		"""
		TODO: Optimize for speed!
		"""

		# Log status
		self.log.out('[routine-server] Trying call routine "%s" ...' % self.name)

		# Unpack passed arguments, handle pointers and structs ...
		args, kw = self.__unpack_arguments__(arg_message_list)

		# Unpack pointer data
		memory_transport_handle = self.server_unpack_memory_list(args, arg_memory_list, self.memsync)

		# Default return value
		return_value = None

		# This is risky
		try:

			# Call into dll
			return_value = self.handler(*tuple(args), **kw)

			# Log status
			self.log.out('[routine-server] ... done.')

		except:

			# Log status
			self.log.out('[routine-server] ... failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

		# Pack memory for return
		return_memory_list = self.server_pack_memory_list(memory_transport_handle)

		try:
			# Pack return package and return it
			return self.__pack_return__(args, kw, return_value, return_memory_list)
		except:
			# Push traceback to log
			self.log.err(traceback.format_exc())


	def __pack_return__(self, args, kw, return_value, return_memory_list):
		"""
		TODO: Optimize for speed!
		"""

		# Start argument list as a list
		arguments_list = []

		# Step through arguments
		for arg_index, arg in enumerate(args):

			# Fetch definition of current argument
			arg_definition_dict = self.argtypes_p[arg_index]

			arg_value = arg # Set up arg for iterative unpacking
			for flag in arg_definition_dict['f']: # step through flags

				# Handle pointers
				if flag == FLAG_POINTER:

					# There are two ways of getting the actual value
					if hasattr(arg_value, 'value'):
						arg_value = arg_value.value
					elif hasattr(arg_value, 'contents'):
						arg_value = arg_value.contents
					else:
						pass
						# self.log.err(pf(arg_value))
						# raise # TODO

				# Handle arrays
				elif flag > 0:

					arg_value = arg_value[:]

				# Handle unknown flags
				else:

					self.log.err('ERROR in __pack_return__, flag %d' % flag)
					raise # TODO

			self.log.err('   efg')
			self.log.err(pf(arg_value))

			# Handle fundamental types by value
			if arg_definition_dict['g'] == GROUP_FUNDAMENTAL:

				if hasattr(arg_value, 'value'):
					arg_value = arg_value.value
				arguments_list.append(arg_value)

				# # If by reference ...
				# if arg_definition_dict['p']:
				# 	# Append value from ctypes datatype (because most of their Python equivalents are immutable)
				# 	arguments_list.append(arg.value)
				# # If by value ...
				# else:
				# 	# Nothing to do ...
				# 	arguments_list.append(None)

			# Handle everything else (structures etc)
			else:

				# HACK TODO
				arguments_list.append(None)

		return {
			'args': arguments_list,
			'kw': {}, # TODO not yet handled
			'return_value': return_value, # TODO allow & handle pointers
			'memory': return_memory_list
			}


	def register_argtype_and_restype(self, argtypes_p, restype_p, memsync):

		# Log status
		self.log.out('[routine-server] Set argument and return value types for "%s" ...' % self.name)

		# Store memory sync instructions
		self.memsync = memsync

		# Store argtype definition dict
		self.argtypes_p = argtypes_p

		# Parse and apply argtype definition dict to actual ctypes routine
		self.handler.argtypes = self.unpack_definition_argtypes(argtypes_p)

		# Store return value definition dict
		self.restype_p = restype_p

		# Parse and apply restype definition dict to actual ctypes routine
		self.handler.restype = self.unpack_definition_returntype(restype_p)

		# Log status
		self.log.out('[routine-server] ... memsync: %s ...' % pf(self.memsync))
		self.log.out('[routine-server] ... argtypes: %s ...' % pf(self.handler.argtypes))
		self.log.out('[routine-server] ... restype: %s ...' % pf(self.handler.restype))

		# Log status
		self.log.out('[routine-server] ... done.')

		return True # Success


	def __unpack_arguments__(self, args_list):
		"""
		TODO Optimize for speed!
		"""

		# Start argument list as a list (will become a tuple)
		arguments_list = []

		# Step through arguments
		for arg_index, arg in enumerate(args_list):

			# Fetch definition of current argument
			arg_definition_dict = self.argtypes_p[arg_index]

			# Handle fundamental types
			if arg_definition_dict['g'] == GROUP_FUNDAMENTAL:

				try:

					# Start process with plain argument
					arg_rebuilt = getattr(ctypes, arg_definition_dict['t'])(arg[1])

					# Step through flags
					for flag in arg_definition_dict['f']:

						if flag == FLAG_POINTER:

							pass # Nothing to do?

						elif flag > 0:

							raise

						else:

							raise

					# # By reference
					# if arg_definition_dict['p']:
					# 	# Put value back into its ctypes datatype
					# 	arguments_list.append(
					# 		getattr(ctypes, arg_definition_dict['t'])(arg[1])
					# 		)
					# # By value
					# else:
					# 	# Append value
					# 	arguments_list.append(arg[1])

					arguments_list.append(arg_rebuilt)

				except:

					self.log.err('ERROR in __unpack_arguments__, fundamental datatype path')
					self.log.err(traceback.format_exc())

			# Handle structs
			elif arg_definition_dict['g'] == GROUP_STRUCT:

				# Generate new instance of struct datatype
				struct_arg = self.struct_type_dict[arg_definition_dict['t']]()

				# Unpack values into struct
				self.__unpack_arguments_struct__(arg_definition_dict['_fields_'], struct_arg, arg[1])

				# Append struct to list
				arguments_list.append(struct_arg)

			# Handle everything else ...
			else:

				# HACK TODO
				arguments_list.append(0)

		# Return args as tuple and kw as dict
		return arguments_list, {} # TODO kw not yet handled


	def __unpack_arguments_struct__(self, arg_definition_list, struct_inst, args_list):
		"""
		TODO Optimize for speed!
		Can be called recursively!
		"""

		# Step through arguments
		for arg_index, arg in enumerate(args_list):

			# Get current argument definition
			arg_definition_dict = arg_definition_list[arg_index]

			# Handle fundamental types
			if arg_definition_dict['g'] == GROUP_FUNDAMENTAL:

				# Put value back into its ctypes datatype
				setattr(
					struct_inst, # struct instance to be modified
					arg[0], # parameter name (from tuple)
					getattr(ctypes, arg_definition_dict['t'])(arg[1]) # ctypes instance of type with value from tuple
					)

				# TODO pointers and arrays

			# Handle structs
			elif arg_definition_dict['g'] == GROUP_STRUCT:

				# Generate new instance of struct datatype
				struct_arg = self.struct_type_dict[arg_definition_dict['t']]()

				# Unpack values into struct
				self.__unpack_arguments_struct__(arg_definition_dict['_fields'], struct_arg, arg[1])

				# Append struct to struct TODO handle pointer to structs!
				setattr(
					struct_inst, # struct instance to be modified
					arg[0], # parameter name (from tuple)
					struct_arg # value from tuple
					)

			# Handle everything else ...
			else:

				# HACK TODO
				setattr(
					struct_inst, # struct instance to be modified
					arg[0], # parameter name (from tuple)
					0 # least destructive value ...
					)
