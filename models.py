from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flaskapp import db
from datetime import datetime
from json import dumps
from binascii import hexlify
from os import urandom

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True)
	email = db.Column(db.String(120), unique=True)
	confirmed = db.Column(db.Boolean)
	secret = db.Column(db.String(52))
	created = db.Column(db.DateTime)
	level = db.Column(db.Integer)
	password = db.Column(db.String(100))
	servers = db.relationship('GameServer', backref='user', lazy='dynamic')
	accounts = db.relationship('Account', backref='user', lazy='dynamic')
	leaderboards = db.relationship('LeaderBoard', backref='user', lazy='dynamic')

	def __init__(self, username, email, password, level=1):
		self.username = username
		self.email = email
		self.level = level
		self.confirmed = False
		self.password = generate_password_hash(password)
		self.created = datetime.utcnow()

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def gen_secret(self, db):
		self.secret = str(self.id).zfill(4) + hexlify(urandom(24)).decode()
		db.session.commit()

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return str(self.id)


class GameServer(db.Model):
	__tablename__ = 'servers'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40))
	secret = db.Column(db.String(8))
	min_clients = db.Column(db.Integer)
	min_stop = db.Column(db.Integer)
	max_clients = db.Column(db.Integer)
	created = db.Column(db.DateTime)
	setup = db.Column(db.Boolean)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	instances = db.relationship('Instance', backref='server', lazy='dynamic')
	max_instances = db.Column(db.Integer)

	def __init__(self, user, name, min_clients, max_clients, min_stop, max_instances):
		self.name = name
		self.min_clients = min_clients
		self.max_clients = max_clients
		self.min_stop = min_stop
		self.max_instances = max_instances
		self.created = datetime.utcnow()
		self.setup = False
		user.servers.append(self)

	def __repr__(self):
		return '<Game Server {}>'.format(self.name)

	def gen_secret(self, db):
		self.secret = "GS" + str(self.id).zfill(2) + hexlify(urandom(2)).decode()
		db.session.commit()

	def get_gears(self):
		gears = self.max_instances * 6
		if self.max_clients - 2 > 0:
			gears += self.max_instances * (self.max_clients - 2) * 2
		if self.min_stop == 0:
			gears += 2
		return gears

	def get_running(self):
		return len(self.instances.filter_by(stop=None).all())

	def get_state(self):
		if self.setup == False:
			return "error"
		else:
			return "good"



class Account(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True)
	email = db.Column(db.String(120))
	password = db.Column(db.String(66))
	data = db.Column(db.Text)
	created = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	def __init__(self, user, username, password, email="", **kwargs):
		user.accounts.append(self)
		self.username = username
		self.password = generate_password_hash(password)
		self.email = email
		self.created = datetime.utcnow()
		self.data = dumps(kwargs)

	def __repr__(self):
		return '<Account {} of user {}>'.format(self.username, self.user.username)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def encode(self):
		return {"username": self.username, "data": self.data, "created": self.created.isoformat()}

class Instance(db.Model):
	__tablename__ = 'instances'
	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.Integer)
	log = db.Column(db.Text)
	start = db.Column(db.DateTime)
	stop = db.Column(db.DateTime)
	server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))

	def __init__(self, server):
		server.instances.append(self)
		self.number = len(self.server.instances.all())
		self.start = datetime.utcnow()

	def __repr__(self):
		return '<Instance of {}>'.format(self.server)

	def end(self):
		self.stop = datetime.utcnow()
		db.session.commit()

	def encode(self):
		from flaskapp import manager
		if self.id not in manager.servers.keys() and self.stop is None:  # Temp
			self.end()
		if self.stop is not None:
			stop = self.stop.isoformat()
			c = 0
			mc = 0
		else:
			stop = None
			svr = manager.servers[self.id]
			c = len(svr.clients)
			mc = svr.options["max_clients"]

		return {"log": self.log, "start": self.start.isoformat(), "stop": stop, "id": self.number, "clients": c, "max_clients": mc}

class LeaderBoard(db.Model):
	__tablename__ = 'leaderboards'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40))
	secret = db.Column(db.String(8))
	created = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	items = db.relationship('LeaderBoardItem', backref='leaderboard', lazy='dynamic')

	def __init__(self, user, name):
		self.name = name
		self.created = datetime.utcnow()
		user.leaderboards.append(self)

	def __repr__(self):
		return '<Leaderboard {}>'.format(self.name)

	def gen_secret(self, db):
		self.secret = "LB" + str(self.id).zfill(2) + hexlify(urandom(2)).decode()
		db.session.commit()

	def encode(self):
		items = [[i.key, i.value] for i in self.items.all()]
		return {'name': self.name, 'secret': self.secret, 'items': items}

	def add(self, key, value):
		LeaderBoardItem(self, key, str(value))
		db.session.commit()

class LeaderBoardItem(db.Model):
	__tablename__ = "leaderboard_items"
	id = db.Column(db.Integer, primary_key=True)
	key = db.Column(db.String(40))
	value = db.Column(db.String(40))
	added = db.Column(db.DateTime)
	leaderboard_id = db.Column(db.Integer, db.ForeignKey('leaderboards.id'))

	def __init__(self, leaderboard, key, value):
		self.key = key
		self.value = value
		self.added = datetime.utcnow()
		leaderboard.items.append(self)

	def __repr__(self):
		return '<{}: {} of Leaderboard {}>'.format(self.key, self.value, self.leaderboard.name)


def init_db():
	db.reflect()
	db.drop_all()
	db.create_all()

def test():
	u = User("uname", "mail", "pword")
	db.session.add(u)

	g = GameServer(u, "gname", "scrt", 2, 3, True, False)
	db.session.add(g)

	db.session.commit()
