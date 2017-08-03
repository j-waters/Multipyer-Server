from json import dumps, loads

class Payload:
	def __init__(self, decode=None, **kwargs):
		self.action = None
		if type(decode) == dict:
			self.__dict__.update(decode)
		if type(decode) == str:
			self.__dict__.update(loads(decode))

		self.__dict__.update(kwargs)

		if not hasattr(self, 'origin'):
			self.origin = "s"

	def encode(self):
		return dumps(self.__dict__)
