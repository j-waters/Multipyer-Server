import gevent
from geventwebsocket.websocket import WebSocket, WebSocketError
import locals
from payload import Payload
from flaskapp import socketio


class Client:
	def __init__(self, master, socket, unid):
		self.master = master
		self.socket = socket  # type: WebSocket
		self.unid = unid
		self.data = {}
		self.outQueue = []
		self.handshake()

	def handshake(self):
		p = Payload(action=locals.HANDSHAKE, unid=self.unid)
		self.send(p)
		# gevent.spawn(self._queue)
		if not type(self.socket) == str:
			gevent.spawn(self._poll)

	def _send(self, payload):
		if type(self.socket) == str:
			try:
				socketio.emit('send', payload.encode(), namespace="/serverio", room=self.socket)
				self.outQueue.remove(payload)
			except ValueError:
				pass
		else:
			try:
				#print("SEND:", payload.encode())
				self.socket.send(payload.encode())
				self.outQueue.remove(payload)
			except WebSocketError:
				self.master.kill(self)
				self.outQueue.remove(payload)

	def send(self, payload):
		self.outQueue.append(payload)
		#while len(self.outQueue) > 0:
		gevent.spawn(self._send, self.outQueue[0])
			#gevent.sleep(1)

	def _receive(self):
		try:
			data = self.socket.receive()
			if data is None:
				raise WebSocketError
			data = Payload(data)
			#print("RECV:", data.__dict__)
			self.master.inQueue.append(data)
		except WebSocketError:
			self.master.kill(self)

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

	def encode(self):
		out = {"unid": self.unid}
		out.update(self.data)
		return out
