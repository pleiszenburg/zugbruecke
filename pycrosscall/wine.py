# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import subprocess


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE SESSION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class wine_session_class:

	def __init__(self, session_id):

		self.id = session_id

		print('UNIX (%s): wine session started' % self.id)


	def terminate(self):

		print('UNIX (%s): wine session terminated' % self.id)


	def translate_path_unix2win(self, path):

		winepath_p = subprocess.Popen(
			['winepath', '-w', path],
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE
			)
		wine_out, wine_err = winepath_p.communicate()

		return wine_out.decode(encoding = 'UTF-8').strip(), wine_err.decode(encoding = 'UTF-8')
