# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import json
import re
import sys
import time


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
			self.f['out'] = open('%s_%s.txt' % (self.p['platform'], 'out'), 'w+', buffering = 1)
			self.f['err'] = open('%s_%s.txt' % (self.p['platform'], 'err'), 'w+', buffering = 1)


	def terminate(self):

		if self.up:
			if self.p['logwrite']:
				self.f['out'].close()
				self.f['err'].close()
			self.up = False


	def __compile_message_dict__(self, message, pipe_name):

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


	def __print_messages__(self, messages):

		for message_item in messages:
			if self.p['std' + message_item['pipe']]:
				message_string = '%s (%s @ %.2f) %s: %s\n' % (
					message_item['platform'],
					message_item['id'],
					message_item['time'],
					message_item['pipe'],
					message_item['cnt']
					)
				if message_item['pipe'] == 'out':
					sys.stdout.write(message_string)
				elif message_item['pipe'] == 'err':
					sys.stderr.write(message_string)
				else:
					raise # TODO


	def __store_messages__(self, messages):

		for message_item in messages:
			self.f[message_item['pipe']].write(json.dumps(message_item) + '\n')


	def __append_to_log__(self, messages):

		for message_item in messages:
			self.log[message_item['pipe']].append(message_item)


	def __process_message__(self, message, pipe):

		message_dict_list = self.__compile_message_dict__(message, pipe)
		self.__append_to_log__(message_dict_list)
		self.__print_messages__(message_dict_list)
		if self.p['logwrite']:
			self.__store_messages__(message_dict_list)


	def out(self, message, source = ''):

		if source != '':
			print('out ' + message)

		self.__process_message__(message, 'out')


	def err(self, message, source = ''):

		if source != '':
			print('err ' + message)

		self.__process_message__(message, 'err')
