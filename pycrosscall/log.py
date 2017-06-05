# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LOG CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class log_class:


	def __init__(self, session_id, parameter):

		self.id = session_id
		self.p = parameter

		# Start arrays for stdout and stderr logs
		self.log_out = []
		self.log_err = []

		# Determine platform
		if 'platform' not in self.p.keys():
			self.p['platform'] = 'UNIX'


	def out(self, message):

		# Add lines to log
		for line in message.split('\n'):

			if line.strip() != '':

				self.log_out.append(line)

				if self.p['stdout']:
					print('%s (%s) out: %s' % (self.p['platform'], self.id, line))


	def err(self, message):

		# Add lines to log
		for line in message.split('\n'):

			if line.strip() != '':

				self.log_err.append(line)

				if self.p['stderr']:
					print('%s (%s) err: %s' % (self.p['platform'], self.id, line))
