# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	pycrosscall/log.py: Classes for gathering, managing and displaying logs

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

import json
import re
import sys
import threading
import time

try:
	from .lib import get_free_port
	from .rpc import (
		xmlrpc_client,
		xmlrpc_requesthandler,
		xmlrpc_server
		)
except:
	from lib import get_free_port
	from rpc import (
		xmlrpc_client,
		xmlrpc_requesthandler,
		xmlrpc_server
		)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONSTANTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# https://en.wikipedia.org/wiki/ANSI_escape_code
c = {
	'RESET': '\033[0;0m',
	'BOLD': '\033[;1m',
	'REVERSE': '\033[;7m',
	'GREY': '\033[1;30m',
	'RED': '\033[1;31m',
	'GREEN': '\033[1;32m',
	'YELLOW': '\033[1;33m',
	'BLUE': '\033[1;34m',
	'MAGENTA': '\033[1;35m',
	'CYAN': '\033[1;36m',
	'WHITE': '\033[1;37m'
	}


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LOG CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class log_class:


	def __init__(self, session_id, parameter):

		# Store id and parameter
		self.id = session_id
		self.p = parameter

		# Log is up
		self.up = True

		# Start arrays for stdout and stderr logs
		self.log = {}
		self.log['out'] = []
		self.log['err'] = []

		# Determine platform
		if 'platform' not in self.p.keys():
			self.p['platform'] = 'UNIX'

		# Open logfiles
		if self.p['logwrite']:
			self.f = {}
			self.f['out'] = '%s_%s.txt' % (self.p['platform'], 'out')
			self.f['err'] = '%s_%s.txt' % (self.p['platform'], 'err')

		# Fire up server if required
		self.server_port = 0
		if self.p['log_server']:
			self.__start_server__()

		# Fire up client if required
		if self.p['remote_log']:
			self.__start_client__()


	def terminate(self):

		if self.up:

			# Stop server, if there is one
			if self.p['log_server']:
				self.__stop_server__()

			# Log down
			self.up = False


	def __append_message_to_log__(self, message):

		self.log[message['pipe']].append(message)


	def __compile_message_dict_list__(self, message, pipe_name, level):

		message_lines = []
		message_line_max = 80

		for line in message.split('\n'):
			if line.strip() != '':
				message_lines.append({
					'level': level,
					'platform': self.p['platform'],
					'id': self.id,
					'time': round(time.time(), 2),
					'pipe': pipe_name,
					'cnt': line
					})

		return message_lines


	def __print_message__(self, messages):

		message_list = []

		message_list.append(c['GREY'] + '(%.2f/%s) ' % (messages['time'], messages['id']) + c['RESET'])
		if messages['platform'] == 'UNIX':
			message_list.append(c['BLUE'])
		elif messages['platform'] == 'WINE':
			message_list.append(c['MAGENTA'])
		else:
			message_list.append(c['WHITE'])
		message_list.append('%s ' % messages['platform'] + c['RESET'])
		if messages['pipe'] == 'out':
			message_list.append(c['GREEN'])
		elif messages['pipe'] == 'err':
			message_list.append(c['RED'])
		message_list.append(messages['pipe'][0] + c['RESET'])
		message_list.append(': ')
		if any(ext in messages['cnt'] for ext in ['fixme:', 'err:', 'wine client error']):
			message_list.append(c['GREY'])
		else:
			message_list.append(c['WHITE'])
		message_list.append(messages['cnt'] + c['RESET'])
		message_list.append('\n')

		message_string = ''.join(message_list)

		if messages['pipe'] == 'out':
			sys.stdout.write(message_string)
		elif messages['pipe'] == 'err':
			sys.stderr.write(message_string)
		else:
			raise # TODO


	def __process_message__(self, message, pipe, level):

		message_dict_list = self.__compile_message_dict_list__(message, pipe, level)

		for mesage_dict in message_dict_list:

			self.__process_message_dict__(mesage_dict)


	def __process_message_dict__(self, mesage_dict):

			self.__append_message_to_log__(mesage_dict)
			if self.p['std' + mesage_dict['pipe']]:
				self.__print_message__(mesage_dict)
			if self.p['remote_log']:
				self.__push_message_to_server__(mesage_dict)
			if self.p['logwrite']:
				self.__store_message__(mesage_dict)


	def __push_message_to_server__(self, message):

		self.client.transfer_message(json.dumps(message))


	def __receive_message_from_client__(self, message):

		self.__process_message_dict__(json.loads(message))


	def __start_client__(self):

		self.client = xmlrpc_client('http://localhost:%d' % self.p['port_server_log'])


	def __start_server__(self):

		# Get a free port from the OS
		self.server_port = get_free_port()

		# Create server
		self.server = xmlrpc_server(
			('localhost', self.server_port),
			requestHandler = xmlrpc_requesthandler,
			allow_none = True,
			logRequests = False
			)

		# Register functions
		self.server.register_introspection_functions()
		self.server.register_function(self.__receive_message_from_client__, 'transfer_message')

		# Run server in its own thread
		self.thread_server = threading.Thread(
			target = self.server.serve_forever,
			args = (),
			name = 'server'
			)
		self.thread_server.daemon = True
		self.thread_server.start()


	def __stop_server__(self):

		self.server.shutdown()


	def __store_message__(self, message):

		f = open(self.f[message['pipe']], 'a+')
		f.write(json.dumps(message) + '\n')
		f.close()


	def out(self, message, level = 1):

		if level <= self.p['log_level']:
			self.__process_message__(message, 'out', level)


	def err(self, message, level = 1):

		if level <= self.p['log_level']:
			self.__process_message__(message, 'err', level)
