#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import atexit
# import os
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
		self.log = log_class(self.id, parameter = {'platform': 'WINE', 'stdout': True, 'stderr': True}) # HACK pass from UNIX

		# Status log
		self.log.out('Wine-Python started')

		# Register session destructur
		atexit.register(self.terminate)

		# Create server
		self.server = SimpleXMLRPCServer(("localhost", 8000), requestHandler = RequestHandler)

		# TODO register functions

		# Run the server's main loop
		self.server.serve_forever()


	def terminate(self):

		# Status log
		self.log.out('Wine-Python terminating')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# INIT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	if len(sys.argv) > 1:
		print('SESSION ID: "%s"' % sys.argv[1])
		session = wine_server_class(sys.argv[1]) # HACK replace with arg parsing and switch
	else:
		print('ERROR: no session id passed') # TODO raise error
