import flask
from flask_sockets import Sockets
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
sockets = Sockets(app)

app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)

import gevent
import time
from manager import Manager
manager = Manager()
import os
from json import dumps



import models


@sockets.route('/server/<id>/<instance>')
def websocket(ws, id, instance):
	client = manager.add_client(ws)
	if instance:  # id is that of an instance
		pass
	else:  # id is that of a blank server
		manager.add_to_queue(id, client)

	while not client.socket.closed:
		gevent.sleep(0)


@app.route('/')
def home():
	return "Home page coming soon"

@app.route('/connect', methods=['GET', 'POST'])
def connect():
	if flask.request.method == 'GET':
		return flask.redirect(flask.url_for('home'), code=307)
	if flask.request.method == 'POST':
		data = flask.request.form
		gs = models.GameServer.query.filter_by(id=data['gsid']).first()

	return ""