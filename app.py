from flask import Flask
from flask_sockets import Sockets
import gevent

app = Flask(__name__)
sockets = Sockets(app)
class Server():
    def __init__(self):
        self.clients = list()

    def connect(self, client):
        self.clients.append(client)

    def update(self, client, data):
        for c in self.clients:
            if c != client:
                c.send(data)

svr = Server()

@sockets.route('/connect')
def connect(ws):
    svr.connect(ws)
    while not ws.closed:
        message = ws.receive()
        if message:
            gevent.Greenlet.spawn(svr.update, ws, message)

if __name__ == "__main__":
    app.run(port=8000, debug=True)