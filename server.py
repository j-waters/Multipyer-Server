import gevent
from client import Client
from payload import Payload
import models
import locals

class Server:
	def __init__(self, gs):
		self.options = {"max_clients":gs.max_clients,
						"min_clients":gs.min_clients,
						"persistent":gs.persistent,
						"hard_min":gs.hard_min}
		self.clients = {}
		self._curid = 0
		self.inQueue = []
		self.instance = models.Instance(gs)
		gevent.spawn(self.update)


	def process(self, payload):
		pass


	def update(self):
		while True:
			if len(self.inQueue) > 0:
				payload = self.inQueue.pop(0) # type: Payload
				if payload.target == "s":
					self.process(payload)
			gevent.sleep(0)
