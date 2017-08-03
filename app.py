from flask import Flask
from flask_sockets import Sockets
import gevent
import time
from server import Server

app = Flask(__name__)
app.debug = True
sockets = Sockets(app)

svr = Server()

@sockets.route('/connect')
def connect(ws):
	svr.connect(ws)
	while True:
		gevent.sleep(0)

@app.route('/test')
def test():
	return "It Works!"