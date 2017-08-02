import gevent
from geventwebsocket.websocket import WebSocket, WebSocketError
import locals
from payload import Payload

class Client:
	def __init__(self, server, socket, unid):
		self.server = server
		self.socket = socket  # type: WebSocket
		self.unid = unid
		self.connected = False
		self.outQueue = []
		self.handshake()

	def handshake(self):
		p = Payload(action=locals.HANDSHAKE, unid=self.unid)
		self.send(p)
		gevent.spawn(self._queue)
		gevent.spawn(self._poll)

	def _send(self, payload):
		try:
			self.socket.send(payload)
			self.outQueue.remove(payload)
		except WebSocketError:
			print("Socket is dead")

	def send(self, payload):
		self.outQueue.append(payload)

	def _receive(self):
		try:
			recv = self.socket.receive()
			recv = Payload(recv)
			self.server.inQueue.append(recv)
		except WebSocketError:
			print("Socket already closed")

	def _queue(self):
		while True:
			if len(self.outQueue) > 0:
				self.send(self.outQueue[0])
			gevent.sleep(0)

	def _poll(self):
		while True:
			self._receive()
		gevent.sleep(0)