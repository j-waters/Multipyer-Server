import pickle
import flask_sockets

class Server():
    def __init__(self):
        self.clients = list()
        self._curid = 0

    def connect(self, ws):
        self._curid += 1
        client = Client(ws, "c_" + str(self._curid))
        self.clients.append(client)
        return client

    def update(self, client, data):
        for c in self.clients:
            if c != client:
                c.send(data)

class Client():
    def __init__(self, socket, unid):
        self.socket = socket
        self.unid = unid
        self.connected = False

    def handshake(self):
        pass

    def send(self):
        pass