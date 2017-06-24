# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	pycrosscall/dll.py: Classes relevant for managing the access to DLLs

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
from functools import partial
from pprint import pformat as pf

from .lib import FUNDAMENTAL_C_DATATYPES


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LOADLIBRARY CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class dll_session_class(): # Mimic ctypes.WinDLL. Representing one idividual dll to be called into, returned by LoadLibrary


	def __init__(self, full_path_dll, dll_name, dll_type, parent_session):

		# Store dll parameters name, path and type
		self.__dll_full_path__ = full_path_dll
		self.__dll_name__ = dll_name
		self.__dll_type__ = dll_type

		# Store pointer to pycrosscall session
		self.__session__ = parent_session

		# For convenience ...
		self.__client__ = self.__session__.client

		# Start dict for dll routines
		self.__dll_routines__ = {}

		# Translate dll's full path into wine path
		self.__dll_full_path_wine__ = self.__session__.wineserver_session.translate_path_unix2win(self.__dll_full_path__)

		# Status log
		self.__session__.log.out('[00] Telling wine-python about new DLL file: "%s" of type %s' % (
			self.__dll_name__, self.__dll_type__
			))
		self.__session__.log.out('[00] (%s)' % self.__dll_full_path_wine__)

		# Tell wine about the dll and its type
		result = self.__client__.access_dll(
			self.__dll_full_path_wine__, self.__dll_full_path__, self.__dll_name__, self.__dll_type__
			)

		# Raise error if last step failed
		if result == 0:
			raise # TODO


	def __getattr__(self, name): # Handle requests for functions in dll which have yet not been touched

		# Status log
		self.__session__.log.out('[01] Trying to attach to routine "%s" in DLL file "%s" ...' % (name, self.__dll_name__))

		# Is routine unknown?
		if name not in self.__dll_routines__.keys():

			# Log status
			self.__session__.log.out('[02] Routine not yet in list. Registering ...')

			# Register routine in wine
			result = self.__client__.register_routine(self.__dll_full_path__, name)

			# Log status
			self.__session__.log.out('[02] Feedback from wine-python: %d' % result)

			# Raise exception if not found
			if result == 0:
				raise # TODO

			# Add to routine dict
			self.__dll_routines__[name] = {
				'call_handler': partial(self.__handle_call__, __routine_name__ = name),
				'called': False,
				'argtypes': [], # By default, assume no arguments
				'restype': ctypes.c_int # By default, assume no return value
				}

		# Log status
		self.__session__.log.out('[03] Return unconfigured handler for "%s" in DLL file "%s".' % (name, self.__dll_name__))

		# Return handler
		return self.__dll_routines__[name]['call_handler']


	def __handle_call__(self, *args, **kw):

		# Store routine name
		name = kw['__routine_name__']

		# Delete routine name from call parameters
		del kw['__routine_name__']

		# Log status
		self.__session__.log.out('[04] Trying to call routine "%s" in DLL file "%s" ...' % (name, self.__dll_name__))

		# Has this routine ever been called?
		if not self.__dll_routines__[name]['called']:

			# Log status
			self.__session__.log.out('[05] "%s" in DLL file "%s" has not been called before. Configuring ...' % (name, self.__dll_name__))

			# Processing argument and return value types on first call
			self.__set_argtype_and_restype__(name)

			# Tell wine-python about types
			self.__push_argtype_and_restype__(name)

			# Change status of routine - it has been called once and is therefore configured
			self.__dll_routines__[name]['called'] = True

		# Log status
		self.__session__.log.out('[08] Call parameters are %r / %r. Pushing to wine-python ...' % (args, kw))

		# Pack arguments and handle pointers
		arg_message_dict = self.__pack_arguments__(name, args, kw)

		# Actually call routine in DLL! TODO Handle structurs and pointers ...
		return_dict = self.__client__.call_dll_routine(
			self.__dll_full_path__, name, arg_message_dict
			)

		# Unpack return dict (for pointers and structs)
		self.__unpack_return__(name, args, kw, return_dict)

		# Log status
		self.__session__.log.out('[09] Received feedback from wine-python, returning ...')

		# Return result. return_value will be None if there was not a result.
		return return_dict['return_value']


	def __pack_datatype_dict__(self, datatype):

		# Pointer status
		is_pointer = False

		# Get name of datatype
		type_name = datatype.__name__

		# Check for pointer, if yes, flag it and isolate datatype
		if type_name.startswith('LP_'):
			is_pointer = True
			type_name = type_name[3:]

		# Handle cases
		if type_name in FUNDAMENTAL_C_DATATYPES:

			return {
				'p': is_pointer, # Is a pointer
				't': type_name, # Type name, such as 'c_int'
				'f': True # Is a fundamental type
				}

		else:

			raise # TODO


	def __pack_arguments__(self, function_name, args, kw):

		# Shortcut for speed
		arguments_list = []

		# Make it short
		method_metainfo_argtypes = self.__dll_routines__[function_name]['argtypes_p']

		# Step through arguments
		for arg_index, arg in enumerate(args):

			# Fetch definition of current argument
			arg_definition_dict = method_metainfo_argtypes[arg_index]

			# Handle fundamental types by value
			if not arg_definition_dict['p'] and arg_definition_dict['f']:

				# Append value
				arguments_list.append(arg)

			# Handle fundamental types by reference
			elif arg_definition_dict['p'] and arg_definition_dict['f']:

				# Append value from ctypes datatype (because most of their Python equivalents are immutable)
				arguments_list.append(arg.value)

			# Handle everything else (structures)
			else:

				# HACK TODO
				arguments_list.append(None)

		# Return parameter message dict - MUST WORK WITH PICKLE
		return {
			'args': arguments_list,
			'kw': {} # TODO not yet handled
			}


	def __push_argtype_and_restype__(self, name):

		# Log status
		self.__session__.log.out('[07] Processing & pushing argument and return value types ...')

		# Prepare list of arguments by parsing them into list of dicts
		arguments = [self.__pack_datatype_dict__(arg) for arg in self.__dll_routines__[name]['argtypes']]

		# Store processed arguments
		self.__dll_routines__[name]['argtypes_p'] = arguments

		# Parse return type
		returntype = self.__pack_datatype_dict__(self.__dll_routines__[name]['restype'])

		# Store processed return type
		self.__dll_routines__[name]['restype_p'] = returntype

		# Pass argument and return value types as strings ...
		result = self.__client__.register_argtype_and_restype(
			self.__dll_full_path__, name, arguments, returntype
			)

		# Handle error
		if result == 0:
			raise # TODO

		# Log status
		self.__session__.log.out('[07] ... done.')


	def __set_argtype_and_restype__(self, name):

		# TODO proper sanity check
		try:
			self.__dll_routines__[name]['argtypes'] = self.__dll_routines__[name]['call_handler'].argtypes
		except:
			pass
		try:
			self.__dll_routines__[name]['restype'] = self.__dll_routines__[name]['call_handler'].restype
		except:
			pass

		# Log status
		self.__session__.log.out('[06] Set routine "%s" argtypes: %s' % (name, pf(self.__dll_routines__[name]['argtypes'])))
		self.__session__.log.out('[06] Set routine "%s" restype: %s' % (name, pf(self.__dll_routines__[name]['restype'])))


	def __unpack_return__(self, function_name, args, kw, return_dict): # TODO kw not yet handled

		# Get arguments' list
		arguments_list = return_dict['args']

		# Make it short
		method_metainfo_argtypes = self.__dll_routines__[function_name]['argtypes_p']

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
