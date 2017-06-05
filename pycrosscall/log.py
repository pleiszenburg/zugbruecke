
class log_class:


	def __init__(self, session_id):

		self.id = session_id
		self.book = []


	def out(self, message):

		self.book.append(message)
		print('log UNIX (%s): %s' % (self.id, message))
