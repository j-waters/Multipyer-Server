import gevent
from client import Client
from server import Server
import models


class Manager:

	def __init__(self):
		self.queue = {}
		self.instances = []
		self.clients = {}
		self.servers = {}
		self._curid = 0
		gevent.spawn(self.update)

	def add_client(self, ws):
		while True:
			self._curid += 1
			if not self._curid in self.clients.keys():
				unid = "c" + str(self._curid)
				c = Client(self, ws, unid)
				self.clients[unid] = c
				return c

	def add_to_queue(self, gsid, client):
		self.queue[str(gsid)].append(client)

	def create_server(self, gsid):
		gs = models.GameServer.query.filter_by(id=gsid).first()  # type: models.GameServer
		server = Server(gs)


	def update(self):
		while True:
			for gs in self.queue.keys():
				if len(self.queue[str(gs.id)]) >= gs.min_clients:
					self.create_server(gs.id)
			gevent.sleep(0)
