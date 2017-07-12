# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/arg_contents.py: (Un-) packing of argument contents

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

import ctypes
from pprint import pformat as pf

from .const import (
	FLAG_POINTER,
	GROUP_VOID,
	GROUP_FUNDAMENTAL,
	GROUP_STRUCT
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Content packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class arg_contents_class():


	def client_pack_arg_list(self, argtypes_d_sub, args):
		"""
		TODO Optimize for speed!
		Can call itself recursively!
		"""

		# Shortcut for speed
		args_package_list = []

		# Step through arguments
		for arg_index, argtype_d in enumerate(argtypes_d_sub):

			# Fetch current argument by index from tuple or by name from struct/kw
			if type(args) is list or type(args) is tuple:
				arg = args[arg_index]
			else:
				arg = getattr(args, argtype_d['n'])

			# TODO:
			# append tuple to list "args_package_list"
			# tuple contains: (argtype_d['n'], argument content / value)
			#  pointer: arg.value or arg.contents.value
			#  (value: Append value from ctypes datatype, because most of their Python equivalents are immutable)
			#  (contents.value: Append value from ctypes datatype pointer ...)
			#  by value: just "arg"

			try:

				arg_value = arg # Set up arg for iterative unpacking
				for flag in argtype_d['f']: # step through flags

					# Handle pointers
					if flag == FLAG_POINTER:

						# There are two ways of getting the actual value
						if hasattr(arg_value, 'value'):
							arg_value = arg_value.value
						elif hasattr(arg_value, 'contents'):
							arg_value = arg_value.contents
						else:
							raise # TODO

					# Handle arrays
					elif flag > 0:

						arg_value = arg_value[:]

					# Handle unknown flags
					else:

						raise # TODO
			except:

				self.log.err(pf(arg_value))

			self.log.err('   abc')
			self.log.err(pf(arg_value))

			# Handle fundamental types
			if argtype_d['g'] == GROUP_FUNDAMENTAL:

				# Append argument to list ...
				args_package_list.append((argtype_d['n'], arg_value))

			# Handle structs
			elif argtype_d['g'] == GROUP_STRUCT:

				# Reclusively call this routine for packing structs
				args_package_list.append((argtype_d['n'], self.client_pack_arg_list(
					argtype_d['_fields_'], arg
					)))

			# Handle everything else ... likely pointers handled by memsync
			else:

				# Just return None - will (hopefully) be overwritten by memsync
				args_package_list.append(None)

		# Return parameter message list - MUST WORK WITH PICKLE
		return args_package_list


	def client_unpack_return_list(self, argtypes_d, args, return_dict):
		"""
		TODO Optimize for speed!
		"""

		# Get arguments' list
		arguments_list = return_dict['args']

		# Step through arguments
		for arg_index, arg in enumerate(args):

			# Fetch definition of current argument
			arg_definition_dict = argtypes_d[arg_index]

			# Handle fundamental types
			if arg_definition_dict['g'] == GROUP_FUNDAMENTAL:

				# Start process with plain old argument
				arg_value = args[arg_index]
				# New value is: arguments_list[arg_index]

				# Step through flags
				for flag in arg_definition_dict['f']:

					# Handle pointers
					if flag == FLAG_POINTER:

						# There are two ways of getting the actual value
						# if hasattr(arg_value, 'value'):
						# 	arg_value = arg_value.value
						if hasattr(arg_value, 'contents'):
							arg_value = arg_value.contents
						else:
							arg_value = arg_value

					# Handle arrays
					elif flag > 0:

						arg_value = arg_value

					# Handle unknown flags
					else:

						raise # TODO

				if hasattr(arg_value, 'value'):
					arg_value.value = arguments_list[arg_index]
				else:
					arg_value = arguments_list[arg_index]

				# # If by reference ...
				# if arg_definition_dict['p']:
				# 	# Put value back into its ctypes datatype
				# 	args[arg_index].value = arguments_list[arg_index]
				# # If by value
				# else:
				# 	# Nothing to do
				# 	pass

			# Handle everything else (structures and "the other stuff")
			else:

				# HACK TODO
				pass
