#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import argparse
# import atexit
import os
# import signal
import sys
# import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from log import log_class # HACK pass messages to UNIX


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class RequestHandler(SimpleXMLRPCRequestHandler):


	# Restrict to a particular path.
	rpc_paths = ('/RPC2',)


class SimpleXMLRPCServer_ALT(SimpleXMLRPCServer):


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

		self.up = False
		self.log.out('XMLRPCServer shutting down ...')
		self.parent_terminate_func()
		return 1


	def serve_forever(self):

		while self.up:
			self.handle_request()
		self.log.out('XMLRPCServer terminated')


class wine_server_class:


	def __init__(self, session_id, session_port_in, session_port_out):

		self.id = session_id
		self.log = log_class(self.id, parameter = {
			'platform': 'WINE',
			'stdout': True,
			'stderr': True,
			'logwrite': True,
			'remote_log': True,
			'log_server': False,
			'port_unix': session_port_out
			})

		# Session is up
		self.up = True

		# Status log
		self.log.out('Wine-Python up')

		# Register session destructur
		# atexit.register(self.__terminate__)
		# signal.signal(signal.SIGINT, self.__terminate__)
		# signal.signal(signal.SIGTERM, self.__terminate__)

		# Create server
		self.server = SimpleXMLRPCServer_ALT(("localhost", session_port_in), requestHandler = RequestHandler)
		self.server.set_log(self.log)
		self.server.set_parent_terminate_func(self.__terminate__)

		# TODO register functions
		self.server.register_introspection_functions()
		self.server.register_function(self.server.shutdown, 'terminate')

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

	session = wine_server_class(args.id[0], args.port_in[0], args.port_out[0])
