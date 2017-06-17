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

from xmlrpc.client import ServerProxy as xmlrpc_client
from xmlrpc.server import SimpleXMLRPCServer as xmlrpc_server
from xmlrpc.server import SimpleXMLRPCRequestHandler


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class xmlrpc_requesthandler(SimpleXMLRPCRequestHandler):


	# Restrict to a particular path.
	rpc_paths = ('/RPC2',)


class xmlrpc_server_alternative(xmlrpc_server):


	# Server is by definition up from the beginning
	up = True


	def set_log(self, log):

		# Set log
		self.log = log

		# Status log
		self.log.out('[xmlrpc-server] Log attached.')


	def set_parent_terminate_func(self, func):

		# Set function in parent, which needs to be called on shutdown
		self.parent_terminate_func = func


	def shutdown(self):

		# Run only if session still up
		if self.up:

			# Log status
			self.log.out('[xmlrpc-server] TERMINATING ...')

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
		self.log.out('log-xmlrpc-server terminated')
