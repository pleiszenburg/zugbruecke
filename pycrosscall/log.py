# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import json
import re
import sys
import time

import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SERVER CLASS(ES)
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
		self.log.out('Logging-XMLRPCServer log connected')


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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LOG CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class log_class:


	def __init__(self, session_id, parameter):

		# Store id and parameter
		self.id = session_id
		self.p = parameter

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
		if self.p['log_server']:
			self.__start_server__()

		# Fire up client if required
		if self.p['remote_log']:
			self.__start_client__()


	def terminate(self):

		if self.up:
			self.up = False


	def __append_message_to_log__(self, message):

		self.log[message['pipe']].append(message)


	def __compile_message_dict_list__(self, message, pipe_name):

		message_lines = []
		message_line_max = 80

		for line in message.split('\n'):
			if line.strip() != '':
				for line_chunk in re.findall('.{1,%d}' % message_line_max, line):
					message_lines.append({
						'platform': self.p['platform'],
						'id': self.id,
						'time': round(time.time(), 2),
						'pipe': pipe_name,
						'cnt': line_chunk
						})

		return message_lines


	def __print_message__(self, messages):

		message_string = '%s (%s @ %.2f) %s: %s\n' % (
			messages['platform'],
			messages['id'],
			messages['time'],
			messages['pipe'],
			messages['cnt']
			)
		if messages['pipe'] == 'out':
			sys.stdout.write(message_string)
		elif messages['pipe'] == 'err':
			sys.stderr.write(message_string)
		else:
			raise # TODO


	def __process_message__(self, message, pipe):

		message_dict_list = self.__compile_message_dict_list__(message, pipe)

		for mesage_dict in message_dict_list:
			self.__append_message_to_log__(mesage_dict)
			if self.p['std' + mesage_dict['pipe']]:
				self.__print_message__(mesage_dict)
			if self.p['remote_log']:
				self.__push_message_to_server__(mesage_dict)
			if self.p['logwrite']:
				self.__store_message__(mesage_dict)


	def __push_message_to_server__(self, message):

		pass


	def __receive_messages_from_client__(self, messages):

		pass


	def __start_client__(self):

		self.client = xmlrpc.client.ServerProxy('http://localhost:%d' % self.p['port_unix'])


	def __start_server__(self):

		pass


	def __store_message__(self, message):

		f = open(self.f[message['pipe']], 'a+')
		f.write(json.dumps(message) + '\n')
		f.close()


	def out(self, message):

		self.__process_message__(message, 'out')


	def err(self, message):

		self.__process_message__(message, 'err')
