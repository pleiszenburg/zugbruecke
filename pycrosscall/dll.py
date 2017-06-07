# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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

		# Start dict for dll routines
		self.__dll_routines__ = {}


	def __getattr__(self, name): # Handle requests for functions in dll which have yet not been touched

		# Status log
		self.__session__.log.out('Trying to access routine "%s" in dll file "%s"' % (name, self.__dll_name__))

		# Is routine unknown?
		if name not in self.__dll_routines__.keys():

			# Look for routine in dll
			# CALL TO WINE
			# Raise exception if not found

			# Add to routine dict
			self.__dll_routines__[name] = {}

		# Return handler
		return partial(self.__handle_call__, __routine_name__ = name)


	def __handle_call__(self, *args, **kw):

		routine_name = kw['__routine_name__']
		del kw['__routine_name__']

		self.__session__.log.out('trying to call dll routine: %s' % routine_name)
		self.__session__.log.out('... parameters: %r / %r' % (args, kw))
