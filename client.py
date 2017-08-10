import gevent
from geventwebsocket.websocket import WebSocket, WebSocketError
import locals
from payload import Payload


class Client:
	def __init__(self, master, socket, unid):
		self.master = master
		self.socket = socket  # type: WebSocket
		self.unid = unid
		self.outQueue = []
		self.handshake()

	def handshake(self):
		p = Payload(action=locals.HANDSHAKE, unid=self.unid)
		self.send(p)
		# gevent.spawn(self._queue)
		gevent.spawn(self._poll)

	def _send(self, payload):
		try:
			# print("Send:", payload.encode())
			self.socket.send(payload.encode())
			self.outQueue.remove(payload)
		except WebSocketError:
			print("Socket is dead")

	def send(self, payload):
		self.outQueue.append(payload)
		while len(self.outQueue) > 0:
			gevent.spawn(self._send, self.outQueue[0])

	def _receive(self):
		try:
			data = self.socket.receive()
			if data is None:
				raise WebSocketError
			data = Payload(data)
			self.master.inQueue.append(data)
		except WebSocketError:
			pass

	def _queue(self):
		while not self.socket.closed:
			if len(self.outQueue) > 0:
				self._send(self.outQueue[0])
			gevent.sleep(0)

	def _poll(self):
		while not self.socket.closed:
			self._receive()
			gevent.sleep(0)
		# self.close()
