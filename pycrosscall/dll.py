# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import ctypes
from functools import partial
from pprint import pformat as pf


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
		self.__client__ = self.__session__.wine_session.client

		# Start dict for dll routines
		self.__dll_routines__ = {}

		# Translate dll's full path into wine path
		self.__dll_full_path_wine__ = self.__session__.wine_session.translate_path_unix2win(self.__dll_full_path__)

		# Status log
		self.__session__.log.out('Pushing data to wine: "%s" of type %s' % (
			self.__dll_name__, self.__dll_type__
			))
		self.__session__.log.out(' (%s)' % self.__dll_full_path_wine__)

		# Tell wine about the dll and its type
		result = self.__client__.access_dll(
			self.__dll_full_path_wine__, self.__dll_full_path__, self.__dll_name__, self.__dll_type__
			)

		# Raise error if last step failed
		if result == 0:
			raise # TODO


	def __getattr__(self, name): # Handle requests for functions in dll which have yet not been touched

		# Status log
		self.__session__.log.out('Trying to access routine "%s" in dll file "%s"' % (name, self.__dll_name__))

		# Is routine unknown?
		if name not in self.__dll_routines__.keys():

			# Log status
			self.__session__.log.out('Routine not yet in list. Registering ...')

			# Register routine in wine
			result = self.__client__.register_routine(self.__dll_full_path__, name)

			# Log status
			self.__session__.log.out('Feedback from wine: %d' % result)

			# Raise exception if not found
			if result == 0:
				raise # TODO

			# Add to routine dict
			self.__dll_routines__[name] = {
				'call_handler': partial(self.__handle_call__, __routine_name__ = name),
				'called': False,
				'argtypes': [], # By default, assume no arguments
				'restype': ctypes.c_void_p # By default, assume no return value
				}

		# Return handler
		return self.__dll_routines__[name]['call_handler']


	def __handle_call__(self, *args, **kw):

		# Store routine name
		name = kw['__routine_name__']

		# Delete routine name from call parameters
		del kw['__routine_name__']

		# Has this routine ever been called?
		if not self.__dll_routines__[name]['called']:

			# Processing argument and return value types on first call
			self.__set_argtype_and_restype__(name)

			# Tell wine-python about types
			self.__push_argtype_and_restype__(name)

		# Log status
		self.__session__.log.out('trying to call dll routine: %s' % name)
		self.__session__.log.out('... parameters: %r / %r' % (args, kw))

		# # Actually call routine in DLL! TODO Handle structurs and pointers ...
		# return_value = self.__client__.call_routine(
		# 	self.__dll_full_path__, name, args, kw
		# 	)

		return_value = 1

		# Return something if there is something to return ... TODO improve
		if return_value is not None:
			return return_value


	def __push_argtype_and_restype__(self, name):

		# Log status
		self.__session__.log.out('Pushing argument and return value types ...')

		# Pass argument and return value types as strings ...
		result = self.__client__.register_argtype_and_restype(
			self.__dll_full_path__, name,
			[str(arg).split("'")[1] for arg in self.__dll_routines__[name]['argtypes']],
			str(self.__dll_routines__[name]['restype']).split("'")[1]
			)

		# Handle error
		if result == 0:
			raise # TODO


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
		self.__session__.log.out('Routine "%s" argtypes: %s' % (name, pf(self.__dll_routines__[name]['argtypes'])))
		self.__session__.log.out('Routine "%s" restype: %s' % (name, pf(self.__dll_routines__[name]['restype'])))
