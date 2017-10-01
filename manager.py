import gevent
from client import Client
from server import Server
from payload import Payload
import models
import locals
from flaskapp import app

class Manager:

	def __init__(self):
		self.queue = {}
		self.instances = []
		self.clients = {}
		self.servers = {}
		self._curid = 0
		self.inQueue = []
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
		#print("Queue:", self.queue)

	def create_instance(self, gsid):
		gs = models.GameServer.query.filter_by(id=int(gsid)).first()  # type: models.GameServer
		server = Server(gs, self)
		self.servers[server.instanceID] = server
		return server

	def iorecieve(self, sid, data):
		for client in self.clients.values():
			if client.socket == sid:
				data = Payload(data)
				client.master.inQueue.append(data)

	def kill(self, client):
		for k, v in self.queue.items():
			if client in v:
				v.remove(client)
		del self.clients[client.unid]

	def update(self):
		with app.app_context():
			while True:
				for gsid in self.queue.keys():
					gs = models.GameServer.query.filter_by(id=int(gsid)).first()
					if len(self.queue[gsid]) >= gs.min_clients:
						server = self.create_instance(gsid)
						for i in range(gs.min_clients):
							c = self.queue[gsid].pop(0)
							server.add_client(c)
						server.start()
					else:
						for client in self.queue[gsid]:
							p = Payload(target=client.unid, action=locals.QUEUE, length=len(self.queue[gsid]), position=self.queue[gsid].index(client))
							client.send(p)
				#print(app.process.memory_percent(), app.process.cpu_percent())
				while len(self.inQueue) > 0:
					p = self.inQueue.pop(0)
					if p.action == locals.AUTH:
						client = self.clients[p.origin]
						client.data = p.data
						try:
							user = models.User.query.filter_by(secret=p.user).first()
							server = models.GameServer.query.filter_by(user_id=user.id, secret=p.server).first()
						except AttributeError:
							client.send(Payload(target=client.unid, action=locals.INVALID_SECRET))
							continue

						if p.instance == "n":
							if server.min_clients > 1:
								self.add_to_queue(server.id, client)
							else:
								server = self.create_instance(server.id)
								c = self.clients[p.origin]
								server.add_client(c)
								server.start()
						else:
							self.servers[int(p.instance)].add_client(client, True)

				gevent.sleep(1)
