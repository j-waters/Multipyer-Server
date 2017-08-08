from gevent import monkey
monkey.patch_all()

import flask
from flask_sockets import Sockets
from flask_sqlalchemy import SQLAlchemy
import os

app = flask.Flask(__name__)
sockets = Sockets(app)

try:
	app.config.from_pyfile('config.cfg')
except FileNotFoundError:
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('OPENSHIFT_POSTGRESQL_DB_URL')

db = SQLAlchemy(app)

import gevent
import time
from manager import Manager
manager = Manager()
from json import dumps

import models


@sockets.route('/server/<id>/<instance>')
def websocket(ws, id, instance):
	client = manager.add_client(ws)
	print("Connection from", client.unid)
	if instance == "True":  # id is that of an instance
		pass
	else:  # id is that of a blank server
		manager.add_to_queue(id, client)

	while not client.socket.closed:
		gevent.sleep(10)


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