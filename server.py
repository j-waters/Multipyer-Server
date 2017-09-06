import gevent
from client import Client
from payload import Payload
import models
import locals

class Server:
	def __init__(self, gs):
		self.options = {"max_clients":gs.max_clients,
						"min_clients":gs.min_clients,
						"min_stop":gs.min_stop}
		self.clients = {}
		self._curid = 0
		self.inQueue = []
		self.instance = models.Instance(gs)
		gevent.spawn(self.update)
	
	def add_client(self, client):
		client.master = self
		self.clients[client.unid] = client

	def kill(self, client):
		del self.clients[client.unid]


	def process(self, payload):
		pass


	def update(self):
		while True:
			while len(self.inQueue) > 0:
				payload = self.inQueue.pop(0) # type: Payload
				if payload.target == "s":
					self.process(payload)
				elif payload.target == "all":
					for k, v in self.clients.items():
						if k != payload.origin:
							v.send(payload)
				else:
					self.clients[payload.target].send(payload)
			gevent.sleep(0)

	def start(self):
		for client in self.clients.values():
			p = Payload(action=locals.START, clients=[c.unid for c in self.clients.values() if c != client], origin="s")
			client.send(p)
