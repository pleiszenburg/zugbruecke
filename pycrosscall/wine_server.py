#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import atexit
# import os
import signal
import sys
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

		# Status log
		self.log.out('Wine-Python started')

		# Session is up
		self.up = True

		# Register session destructur
		atexit.register(self.terminate)
		signal.signal(signal.SIGINT, self.terminate)
		signal.signal(signal.SIGTERM, self.terminate)

		# Create server
		self.server = SimpleXMLRPCServer(("localhost", 8000), requestHandler = RequestHandler)

		# TODO register functions

		# Run the server's main loop
		self.server.serve_forever()


	def terminate(self):

		# Run only if session still up
		if self.up:

			# Status log
			self.log.out('Wine-Python terminating')

			# Terminate log
			self.log.terminate()

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
