#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import argparse
import ctypes
import os
import sys
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from log import log_class # HACK pass messages to UNIX


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# XMLRPC SERVER CLASSES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class RequestHandler(SimpleXMLRPCRequestHandler):


	# Restrict to a particular path.
	rpc_paths = ('/RPC2',)


class SimpleXMLRPCServer_ALT(SimpleXMLRPCServer):


	# Server is by definition up from the beginning
	up = True


	def set_log(self, log):

		# Set log
		self.log = log

		# Status log
		self.log.out('XMLRPCServer log connected')


	def set_parent_terminate_func(self, func):

		# Set function in parent, which needs to be called on shutdown
		self.parent_terminate_func = func


	def shutdown(self):

		# Run only if session still up
		if self.up:

			# Log status
			self.log.out('XMLRPCServer shutting down ...')

			# Sever is marked down
			self.up = False

			# Tell parent to terminate
			self.parent_terminate_func()

		# Return success, expected default behavior of SimpleXMLRPCServer
		return 1


	def serve_forever(self):

		# Request handler loop
		while self.up:

			# Handle requests ...
			self.handle_request()

		# Log status
		self.log.out('XMLRPCServer terminated')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class wine_server_class:


	def __init__(self, session_id, session_port_in, session_port_out):

		# Store session id
		self.id = session_id

		# Start logging session and connect it with log on unix side
		self.log = log_class(self.id, parameter = {
			'platform': 'WINE',
			'stdout': False,
			'stderr': False,
			'logwrite': True,
			'remote_log': True,
			'log_server': False,
			'port_unix': session_port_out
			})

		# Mark session as up
		self.up = True

		# Status log
		self.log.out('Wine-Python up')

		# Start dict for dll files and routines
		self.dll_dict = {}

		# Create server
		self.server = SimpleXMLRPCServer_ALT(("localhost", session_port_in), requestHandler = RequestHandler)
		self.server.set_log(self.log)
		self.server.set_parent_terminate_func(self.__terminate__)

		# Allow inspection of routines offered by server
		self.server.register_introspection_functions()

		# Register call: Accessing a dll
		self.server.register_function(self.__access_dll__, 'access_dll')
		# Register call: Registering dll calls
		self.server.register_function(self.__register_routine__, 'register_routine')
		# Register destructur: Call goes into xmlrpc-server first, which then terminates parent
		self.server.register_function(self.server.shutdown, 'terminate')

		# Status log
		self.log.out('XMLRPCServer starting ...')

		# Run server ...
		self.server.serve_forever()


	def __access_dll__(self, full_path_dll, dll_name, dll_type):

		# Although this should happen only once per dll, lets be on the safe side
		if full_path_dll not in self.dll_dict.keys():

			# Log status
			self.log.out('Attaching to "%s" of type %s (%s) ...' % (dll_name, dll_type, full_path_dll))

			try:

				# Load library TODO do this for different types of dlls (cdll, oledll)
				self.dll_dict[full_path_dll] = {
					'type': dll_type,
					'name': dll_name,
					'full_path': full_path_dll,
					'handler': ctypes.windll.LoadLibrary(full_path_dll)
					}

				# Log status
				self.log.out(' ... done.')

			except:

				# Log status
				self.log.out(' ... failed!')

				return 0

		return 1 # Success: 1; Fail: 0


	def __register_routine__(self, routine_name):

		# Log status
		self.log.out('Trying to access "%s"' % routine_name)

		# self.dll_dict

		return 1 # Success: 1; Fail: 0


	def __terminate__(self):

		# Run only if session still up
		if self.up:

			# Status log
			self.log.out('Wine-Python terminating ...')

			# Terminate log
			self.log.terminate()

			# Status log
			self.log.out('Wine-Python terminated')

			# Session down
			self.up = False


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
		'--port_in', type = int, nargs = 1
		)
	parser.add_argument(
		'--port_out', type = int, nargs = 1
		)
	args = parser.parse_args()

	# Fire up wine server session with parsed parameters
	session = wine_server_class(args.id[0], args.port_in[0], args.port_out[0])
