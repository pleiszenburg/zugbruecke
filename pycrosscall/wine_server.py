#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import argparse
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

		# Sever is marked down
		self.up = False

		# Log status
		self.log.out('XMLRPCServer shutting down ...')

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

		# Create server
		self.server = SimpleXMLRPCServer_ALT(("localhost", session_port_in), requestHandler = RequestHandler)
		self.server.set_log(self.log)
		self.server.set_parent_terminate_func(self.__terminate__)

		# Register infrastructure functions
		self.server.register_introspection_functions()
		self.server.register_function(self.server.shutdown, 'terminate')

		# TODO register more functions

		# Status log
		self.log.out('XMLRPCServer starting ...')

		# Run server ...
		self.server.serve_forever()


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
