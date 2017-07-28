from flask import Flask
from flask_sockets import Sockets
import gevent
from classes import *

app = Flask(__name__)
sockets = Sockets(app)

svr = Server()

@sockets.route('/connect')
def connect(ws):
    svr.connect(ws)
    print(type(ws))
    while not ws.closed:
        message = ws.receive()
        if message:
            gevent.Greenlet.spawn(svr.update, ws, message)

if __name__ == "__main__":
    app.run(port=8000, debug=True)