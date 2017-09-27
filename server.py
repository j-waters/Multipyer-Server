import gevent
from client import Client
from payload import Payload
import models
import locals
from flaskapp import db, app

class Server:
	def __init__(self, gs, manager):
		self.options = {"max_clients":gs.max_clients,
						"min_clients":gs.min_clients,
						"min_stop":gs.min_stop}
		self.clients = {}
		self._curid = 0
		self.inQueue = []
		instance = models.Instance(gs)
		self.manager = manager
		db.session.add(instance)
		db.session.commit()
		self.instanceID = instance.id
		gevent.spawn(self.update)
	
	def add_client(self, client, new=False):
		client.master = self
		if new:
			for c in self.clients.values():
				p = Payload(action=locals.CLIENTJOIN, unid=client.unid)
				c.send(p)
		self.clients[client.unid] = client


	def kill(self, client):
		del self.clients[client.unid]
		self.check_alive()

	def check_alive(self):
		with app.app_context():
			if len(self.clients.keys()) < self.options["min_stop"]:
				inst = models.Instance.query.filter_by(id=self.instanceID).first()
				inst.end()
				#del self.manager.servers[self.instance.id] # This for some reason causes the database to lock

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
			p = Payload(action=locals.START, clients=[c.unid for c in self.clients.values() if c != client], instance=self.instanceID, origin="s")
			client.send(p)
