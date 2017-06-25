# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	pycrosscall/dll_client.py: Classes relevant for managing the access to DLLs

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

import ctypes
from pprint import pformat as pf

from .routine_client import routine_client_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL CLIENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class dll_client_class(): # Representing one idividual dll to be called into, returned by LoadLibrary


	def __init__(self, full_path_dll, dll_name, dll_type, parent_session):

		# Store dll parameters name, path and type
		self.full_path = full_path_dll
		self.name = dll_name
		self.calling_convention = dll_type

		# Store pointer to pycrosscall session
		self.session = parent_session

		# For convenience ...
		self.client = self.session.client

		# Get handle on log
		self.log = self.session.log

		# Start dict for dll routines
		self.routines = {}

		# Translate dll's full path into wine path
		self.full_path_wine = self.session.wineserver_session.translate_path_unix2win(self.full_path)

		# Status log
		self.log.out('[dll-client] New DLL file "%s" with calling convention "%s" located at' % (
			self.name, self.calling_convention
			))
		self.log.out('[dll-client]  %s' % self.full_path_wine)

		# Tell wine about the dll and its type
		result = self.client.access_dll(
			self.full_path_wine, self.full_path, self.name, self.calling_convention
			)

		# Raise error if last step failed
		if result == 0:
			raise # TODO


	def __getattr__(self, name): # Handle requests for functions in dll which have yet not been touched

		# Status log
		self.log.out('[dll-client] Trying to attach to routine "%s" in DLL file "%s" ...' % (name, self.name))

		# Is routine unknown?
		if name not in self.routines.keys():

			# Create new instance of routine_client
			self.routines[name] = routine_client_class(self, name)

		# Log status
		self.log.out('[dll-client] ... return handler for "%s" in DLL file "%s".' % (name, self.name))

		# Return handler
		return self.routines[name].handle_call


	


	def __pack_datatype_dict__(self, datatype, field_name = None):

		# Pointer status
		is_pointer = False
		# Struct status
		is_struct = False

		# Get name of datatype
		type_name = datatype.__name__
		# Get group of datatype
		group_name = type(datatype).__name__ # 'PyCSimpleType', 'PyCStructType' or 'PyCPointerType'

		# Check for pointer, if yes, flag it and isolate datatype
		if group_name == 'PyCPointerType':
			is_pointer = True
			type_name = datatype._type_.__name__
			group_name = type(datatype._type_).__name__

		# Fundamental C types
		if group_name == 'PyCSimpleType':

			return {
				'n': field_name, # kw
				'p': is_pointer, # Is a pointer
				't': type_name, # Type name, such as 'c_int'
				'f': True, # Is a fundamental type (PyCSimpleType)
				's': False # Is not a struct
				}

		# Structs
		elif group_name == 'PyCStructType':

			# Get fields
			if is_pointer:
				struct_fields = datatype._type_._fields_
			else:
				struct_fields = datatype._fields_

			return {
				'n': field_name, # kw
				'p': is_pointer, # Is a pointer
				't': type_name, # Type name, such as 'c_int'
				'f': False, # Is a fundamental type (PyCSimpleType)
				's': True, # Is not a struct
				'_fields_': [
					self.__pack_datatype_dict__(field[1], field[0]) for field in struct_fields
					]
				}

		# Pointers of pointers
		elif group_name == 'PyCPointerType':

			self.log.err('ERROR: Unhandled pointer of pointer')
			raise # TODO

		# UNKNOWN stuff
		else:

			self.log.err('ERROR: Unknown class of datatype: "%s"', group_name)
			raise # TODO


	def __pack_args__(self, method_metainfo_argtypes, args): # TODO kw
		"""
		TODO Optimize for speed!
		"""

		# Shortcut for speed
		arguments_list = []

		# # Step through arguments
		# for arg_index, arg in enumerate(args):
		#
		# 	# Fetch definition of current argument
		# 	arg_definition_dict = method_metainfo_argtypes[arg_index]

		# Step through arguments
		for arg_index, arg_definition_dict in enumerate(method_metainfo_argtypes):

			# Fetch current argument
			if type(args) is list or type(args) is tuple:
				arg = args[arg_index]
			else:
				arg = getattr(args, arg_definition_dict['n'])

			# Handle fundamental types
			if arg_definition_dict['f']:

				# If pointer
				if arg_definition_dict['p']:

					# Append value from ctypes datatype (because most of their Python equivalents are immutable)
					arguments_list.append((arg_definition_dict['n'], arg.value))

				# If value
				else:

					# Append value
					arguments_list.append((arg_definition_dict['n'], arg))

			# Handle structs
			elif arg_definition_dict['s']:

				# Reclusively call this routine for packing structs
				arguments_list.append((arg_definition_dict['n'], self.__pack_args__(
					arg_definition_dict['_fields_'], arg
					)))

			# Handle everything else (structures)
			else:

				# HACK TODO
				arguments_list.append(None)

		# Return parameter message list - MUST WORK WITH PICKLE
		return arguments_list


	def __push_argtype_and_restype__(self, name):

		# Log status
		self.log.out('[07] Processing & pushing argument and return value types ...')

		# Prepare list of arguments by parsing them into list of dicts (TODO field name / kw)
		arguments = [self.__pack_datatype_dict__(arg) for arg in self.routines[name]['argtypes']]

		# Store processed arguments
		self.routines[name]['argtypes_p'] = arguments

		# Parse return type
		returntype = self.__pack_datatype_dict__(self.routines[name]['restype'])

		# Store processed return type
		self.routines[name]['restype_p'] = returntype

		# Pass argument and return value types as strings ...
		result = self.client.register_argtype_and_restype(
			self.full_path, name, arguments, returntype
			)

		# Handle error
		if result == 0:
			raise # TODO

		# Log status
		self.log.out('[07] ... done.')


	def __set_argtype_and_restype__(self, name):

		# TODO proper sanity check
		try:
			self.routines[name]['argtypes'] = self.routines[name]['call_handler'].argtypes
		except:
			pass
		try:
			self.routines[name]['restype'] = self.routines[name]['call_handler'].restype
		except:
			pass

		# Log status
		self.log.out('[06] Set routine "%s" argtypes: %s' % (name, pf(self.routines[name]['argtypes'])))
		self.log.out('[06] Set routine "%s" restype: %s' % (name, pf(self.routines[name]['restype'])))


	def __unpack_return__(self, function_name, args, kw, return_dict): # TODO kw not yet handled
		"""
		TODO Optimize for speed!
		"""

		# Get arguments' list
		arguments_list = return_dict['args']

		# Make it short
		method_metainfo_argtypes = self.routines[function_name]['argtypes_p']

		# Step through arguments
		for arg_index, arg in enumerate(args):

			# Fetch definition of current argument
			arg_definition_dict = method_metainfo_argtypes[arg_index]

			# Handle fundamental types by value
			if not arg_definition_dict['p'] and arg_definition_dict['f']:

				# Nothing to do
				pass

			# Handle fundamental types by reference
			elif arg_definition_dict['p'] and arg_definition_dict['f']:

				# Put value back into its ctypes datatype
				args[arg_index].value = arguments_list[arg_index]

			# Handle everything else (structures)
			else:

				# HACK TODO
				pass
