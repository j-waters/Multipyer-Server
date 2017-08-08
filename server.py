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
	
	def add_client(self, client):
		client.server = self
		self.clients[client.unid] = client


	def process(self, payload):
		pass


	def update(self):
		while True:
			if len(self.inQueue) > 0:
				payload = self.inQueue.pop(0) # type: Payload
				if payload.target == "s":
					self.process(payload)
			gevent.sleep(0.1)

	def start(self):
		for client in self.clients.values():
			p = Payload(action=locals.START, clients=[c.unid for c in self.clients.values() if c != client], origin="s")
			client.send(p)
