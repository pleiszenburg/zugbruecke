# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	pycrosscall/_server_.py: Customized XML-RPC classes

	Required to run on platform / side: [UNIX, WINE]

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

from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer as rpc_server
from xmlrpc.server import SimpleXMLRPCRequestHandler

from multiprocessing.connection import Listener
import pickle
from threading import Thread


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND CONSTRUCTOR ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class mp_server_handler_class:


	def __init__(self):

		self.__functions__ = {}


	def register_function(self, function_pointer):

		self.__functions__[function_pointer.__name__] = function_pointer


	def handle_connection(self, connection_client):

		try:

			while True:

				# Receive the incomming message
				function_name, args, kwargs = pickle.loads(connection_client.recv())

				# Run the RPC and send a response
				try:
					r = self.__functions__[function_name](*args,**kwargs)
					connection_client.send(pickle.dumps(r))
				except Exception as e:
					connection_client.send(pickle.dumps(e))

		except EOFError:

			pass


class mp_server_class():


	def __init__(self, socket_path, authkey):

		# Store parameters
		self.up = True
		self.socket_path = socket_path
		self.authkey = authkey

		# Set up handler
		self.handler = mp_server_handler_class()

		# Directly pass functions into handler
		self.register_function = self.handler.register_function


	def terminate(self):

		# Stop the server by killing the loop
		if self.up:
			self.up = False


	def serve_forever(self):

		# Open socket
		self.server = Listener(self.socket_path, authkey = self.authkey)

		# Server while server is up
		while self.up:

			try:

				# Accept new client
				client = sock.accept()

				# Handle incomming message in new thread
				t = Thread(target = self.handler.handle_connection, args = (client,))
				t.daemon = True
				t.start()

			except Exception:

				# TODO just print traceback. Better solution?
				traceback.print_exc()


def rpc_client(address):

	return ServerProxy('http://%s:%d' % address)


class rpc_requesthandler(SimpleXMLRPCRequestHandler):


	# Restrict to a particular path.
	rpc_paths = ('/RPC2',)


class rpc_server_alternative(rpc_server):


	# Server is by definition up from the beginning
	up = True


	def set_log(self, log):

		# Set log
		self.log = log

		# Status log
		self.log.out('[rpc-server] Log attached.')


	def set_parent_terminate_func(self, func):

		# Set function in parent, which needs to be called on shutdown
		self.parent_terminate_func = func


	def shutdown(self):

		# Run only if session still up
		if self.up:

			# Log status
			self.log.out('[rpc-server] TERMINATING ...')

			# Sever is marked down
			self.up = False

			# Tell parent to terminate
			self.parent_terminate_func()

			# Log status
			self.log.out('[rpc-server] TERMINATED.')

		# Return success, expected default behavior of SimpleXMLRPCServer
		return 1


	def serve_forever(self):

		# Request handler loop
		while self.up:

			# Handle requests ...
			self.handle_request()
