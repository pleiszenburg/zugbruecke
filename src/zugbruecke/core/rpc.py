# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/rpc.py: Customized RPC classes

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from multiprocessing.connection import (
	Client,
	Listener
	)
from threading import Thread
import traceback


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND CONSTRUCTOR ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class mp_client_class:


	def __init__(self, socket_path, authkey):

		# Start new client on top of socket
		self.client = Client(socket_path, authkey = authkey.encode('utf-8'))


	def __getattr__(self, name):

		# Handler routine in __getattr__ namespace
		def do_rpc(*args, **kwargs):

			# Send request to server
			self.client.send((name, args, kwargs))
			# Receive answer
			result = self.client.recv()

			# If the answer is an error, raise it
			if isinstance(result, Exception):
				raise result

			# Return answer
			return result

		# Return pointer to handler routine
		return do_rpc


class mp_server_handler_class:


	def __init__(self):

		self.__functions__ = {}


	def register_function(self, function_pointer, public_name = None):

		# Is there a custom public name?
		if public_name is not None:
			function_name = public_name
		else:
			function_name = function_pointer.__name__

		# Register function in dict
		self.__functions__[function_name] = function_pointer


	def handle_connection(self, connection_client):

		try:

			while True:

				# Receive the incomming message
				function_name, args, kwargs = connection_client.recv()

				# Run the RPC and send a response
				try:
					r = self.__functions__[function_name](*args,**kwargs)
					connection_client.send(r)
				except Exception as e:
					connection_client.send(e)

		except EOFError:

			pass


class mp_server_class():


	def __init__(self, socket_path, authkey, log = None, terminate_function = None):

		# Set log, likely None
		self.log = log

		# Status log
		if self.log is not None:
			self.log.out('[mp-server] STARTING ...')
			self.log.out('[mp-server] Log attached.')

		# Store parameters
		self.up = True
		self.socket_path = socket_path
		self.authkey = authkey.encode('utf-8')

		# Set terminate func - to be called on termination. Likely None.
		self.terminate_function = terminate_function

		# Set up handler
		self.handler = mp_server_handler_class()

		# Directly pass functions into handler
		self.register_function = self.handler.register_function

		# Status log
		if self.log is not None:
			self.log.out('[mp-server] STARTED.')


	def terminate(self):

		# Terminate only once
		if self.up:

			# Status log
			if self.log is not None:
				self.log.out('[mp-server] TERMINATING ...')

			# Stop the server by killing the loop
			self.up = False

			# Call terminate function if it exists
			if self.terminate_function is not None:
				self.terminate_function()

			# Status log
			if self.log is not None:
				self.log.out('[mp-server] TERMINATED.')


	def serve_forever(self):

		# Open socket
		self.server = Listener(self.socket_path, authkey = self.authkey)

		# Server while server is up
		while self.up:

			try:

				# Accept new client
				client = self.server.accept()

				# Handle incomming message in new thread
				t = Thread(target = self.handler.handle_connection, args = (client,))
				t.daemon = True
				t.start()

			except Exception:

				# TODO just print traceback. Better solution?
				traceback.print_exc()


	def server_forever_in_thread(self):

		# Start the server in its own thread
		t = Thread(target = self.serve_forever)
		t.daemon = True
		t.start()
