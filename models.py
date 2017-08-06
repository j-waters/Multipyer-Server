from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, \
	 check_password_hash
from app import db
from datetime import datetime


class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(40), unique=True)
	email = db.Column(db.String(120), unique=True)
	confirmed = db.Column(db.Boolean)
	created = db.Column(db.DateTime)
	level = db.Column(db.Integer)
	password = db.Column(db.String(66))
	servers = db.relationship('GameServer', backref='user', lazy='dynamic')

	def __init__(self, username, email, password, level=1):
		self.username = username
		self.email = email
		self.level = level
		self.confirmed = False
		self.password = generate_password_hash(password)
		print(self.password, len(self.password))
		self.created = datetime.utcnow()

	def __repr__(self):
		return '<User {}>'.format(self.username)

"""def set_password(self, password):
		self.pw_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.pw_hash, password)"""


class GameServer(db.Model):
	__tablename__ = 'servers'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40))
	secret = db.Column(db.String(40))
	min_clients = db.Column(db.Integer)
	max_clients = db.Column(db.Integer)
	created = db.Column(db.DateTime)
	hard_min = db.Column(db.Boolean)
	persistent = db.Column(db.Boolean)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	instances = db.relationship('Instance', backref='server', lazy='dynamic')

	def __init__(self, user, name, secret, min_clients, max_clients, hard_min, persistent):
		self.name = name
		self.secret = secret
		self.min_clients = min_clients
		self.max_clients = max_clients
		self.hard_min = hard_min
		self.persistent = persistent
		self.created = datetime.utcnow()
		user.servers.append(self)

	def __repr__(self):
		return '<Game Server {}>'.format(self.name)

class Instance(db.Model):
	__tablename__ = 'instances'
	id = db.Column(db.Integer, primary_key=True)
	log = db.Column(db.Text)
	start = db.Column(db.DateTime)
	stop = db.Column(db.DateTime)
	server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))

	def __init__(self, server):
		server.instances.append(self)
		self.start = datetime.utcnow()

	def __repr__(self):
		return '<Instance of {}>'.format(self.server)

def init_db():
	db.reflect()
	db.drop_all()
	db.create_all()
