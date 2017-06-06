#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# import atexit
# import os
# import signal
import sys
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from log import log_class # HACK pass messages to UNIX


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class RequestHandler(SimpleXMLRPCRequestHandler):


	# Restrict to a particular path.
	rpc_paths = ('/RPC2',)


class wine_server_class:


	def __init__(self, session_id):

		self.id = session_id
		self.log = log_class(self.id, parameter = {
			'platform': 'WINE', 'stdout': True, 'stderr': True, 'logwrite': True
			}) # HACK pass from UNIX

		# Session is up
		self.up = True

		# Status log
		self.log.out('Wine-Python up')

		# Register session destructur
		# atexit.register(self.__terminate__)
		# signal.signal(signal.SIGINT, self.terminate)
		# signal.signal(signal.SIGTERM, self.terminate)

		# Create server
		self.server = SimpleXMLRPCServer(("localhost", 8000), requestHandler = RequestHandler)

		# TODO register functions
		self.server.register_introspection_functions()
		self.server.register_function(self.__terminate__, 'terminate')

		# Status log
		self.log.out('XMLRPCServer starting ...')

		# Set up thread for server's main loop
		self.thread_server = threading.Thread(
			target = self.server.serve_forever,
			args = (),
			name = 'server'
			)
		self.thread_server.daemon = True
		self.thread_server.start()

		# Status log
		self.log.out('XMLRPCServer running')


	def __terminate__(self):

		# Status log
		self.log.out('Wine-Python terminate routine hit')

		# Run only if session still up
		if self.up:

			# Status log
			self.log.out('Wine-Python terminating ...')

			# Shut down server
			self.server.shutdown()
			self.server.server_close()
			self.thread_server.join()

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

	if len(sys.argv) > 1:
		print('SESSION ID: "%s"' % sys.argv[1])
		session = wine_server_class(sys.argv[1]) # HACK replace with arg parsing and switch
	else:
		print('ERROR: no session id passed') # TODO raise error
