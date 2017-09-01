print("IMPORT MANAGER 1")

import gevent
from client import Client
from server import Server
import models

print("IMPORT MANAGER 2")


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
		if not str(gsid) in self.queue.keys():
			self.queue[str(gsid)] = []
		self.queue[str(gsid)].append(client)
		print("Queue:", self.queue)

	def create_server(self, gsid):
		print("Create Server")
		gs = models.GameServer.query.filter_by(id=int(gsid)).first()  # type: models.GameServer
		server = Server(gs)
		return server


	def update(self):
		while True:
			for gsid in self.queue.keys():
				gs = models.GameServer.query.filter_by(id=int(gsid)).first()
				if len(self.queue[gsid]) >= gs.min_clients:
					server = self.create_server(gsid)
					for i in range(gs.min_clients):
						c = self.queue[gsid].pop(0)
						server.add_client(c)

					server.start()
			#print(app.process.memory_percent(), app.process.cpu_percent())

			gevent.sleep(1)
