import json

from gevent import monkey
monkey.patch_all()

import flask
from flask_sockets import Sockets
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import exc as SQLException

app = flask.Flask(__name__)
sockets = Sockets(app)

try:
	app.config.from_pyfile('config.cfg')
except FileNotFoundError:
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('OPENSHIFT_POSTGRESQL_DB_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

import gevent
from manager import Manager
manager = Manager()
from psutil import Process
import locals

import models

app.process = Process(os.getpid())


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


@app.route('/acc_register', methods=['POST'])
def acc_register():
	data = json.loads(flask.request.json)
	user = models.User.query.filter_by(secret=data['secret']).first()
	if data["email"] != "":
		m = models.Account.query.filter_by(user=user, email=data["email"]).all()
		if len(m) > 0:
			return str(locals.REG_ETAKEN)
	try:
		a = models.Account(user, **data)
		db.session.add(a)
		db.session.commit()
		print("Registered new user")
		return str(locals.SUCCESS)
	except SQLException.IntegrityError as e:
		print(e)
		return str(locals.REG_TAKEN)
	return locals.FAILURE



@app.route('/connect', methods=['GET', 'POST'])
def connect():
	if flask.request.method == 'GET':
		return flask.redirect(flask.url_for('home'), code=307)
	if flask.request.method == 'POST':
		data = flask.request.form
		gs = models.GameServer.query.filter_by(id=data['gsid']).first()

	return ""


def init():
	db.reflect()
	db.drop_all()
	db.create_all()

	u = models.User("bob", "mail", "123")
	db.session.add(u)

	g = models.GameServer(u, "fun", 2, 2, True, False)
	db.session.add(g)

	db.session.commit()
	print("Database Setup Complete")

#init()