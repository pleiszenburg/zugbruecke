# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LOG CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class log_class:


	def __init__(self, session_id, parameter):

		self.id = session_id
		self.p = parameter

		self.log_out = []
		self.log_err = []


	def out(self, message):

		for line in message.split('\n'):

			if line.strip() != '':

				self.log_out.append(line)

				if self.p['stdout']:
					print('UNIX (%s) out: %s' % (self.id, line))


	def err(self, message):

		for line in message.split('\n'):

			if line.strip() != '':

				self.log_err.append(line)

				if self.p['stderr']:
					print('UNIX (%s) err: %s' % (self.id, line))
