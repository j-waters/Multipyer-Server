import gevent
from client import Client
from payload import Payload
import locals

class Server:
	def __init__(self):
		self.clients = {}
		self._curid = 0
		self.inQueue = []
		gevent.spawn(self.update)

	def connect(self, ws):
		self._curid += 1,
		unid = "c" + str(self._curid)
		client = Client(self, ws, unid)
		self.clients[unid] = client
		return client

	def process(self, payload):
		if payload.action == locals.HANDSHAKE:
			if self.clients[payload.origin].unid == payload.unid:
				self.clients[payload.origin].connected = True


	def update(self):
		while True:
			if len(self.inQueue) > 0:
				payload = self.inQueue.pop(0) # type: Payload
				if payload.target == "s":
					self.process(payload)
		gevent.sleep(0)