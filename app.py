from json import dumps, loads

from gevent import monkey

monkey.patch_all()

import flask
from flask_sockets import Sockets
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import flask_login
import os
from sqlalchemy import exc as SQLException

app = flask.Flask(__name__)
sockets = Sockets(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

try:
	app.config.from_pyfile('config.cfg')
except FileNotFoundError:
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('OPENSHIFT_POSTGRESQL_DB_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret key'

db = SQLAlchemy(app)

import gevent
from manager import Manager

manager = Manager()
from psutil import Process
import locals

import models

app.process = Process(os.getpid())


@sockets.route('/server/')
def websocket(ws):
	client = manager.add_client(ws)
	print("Connection from", client.unid)

	while not client.socket.closed:
		gevent.sleep(10)


@app.route('/console')
@flask_login.login_required
def console():
	return flask.render_template('console.html')


@app.route('/')
def home():
	return flask.render_template('home.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
	if flask.request.method == 'GET':
		return flask.render_template('login.html', failed='False')
	username = flask.request.form['username']
	password = flask.request.form['password']

	user = models.User.query.filter_by(username=username).first()
	if user is None or user.check_password(password) == False:
		return flask.render_template('login.html', failed='True')
	flask_login.login_user(user, remember='remember_me' in flask.request.form)
	return flask.redirect(flask.request.args.get('next') or flask.url_for('console'))

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('home'))

@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))


@app.route('/register', methods=['POST', 'GET'])
def register():
	if flask.request.method == 'GET':
		return flask.render_template('register.html')
	if flask.request.method == 'POST':
		if flask.request.form['username'] == "":
			return message(message="<p>Make sure you enter a username</p>", url=flask.url_for('register'))
		if flask.request.form['email'] == "":
			return message(message="<p>Make sure you enter an email</p>", url=flask.url_for('register'))
		if flask.request.form['password'] == "":
			return message(message="<p>Make sure you enter a password</p>", url=flask.url_for('register'))
		try:
			u = models.User(flask.request.form['username'], flask.request.form['email'], flask.request.form['password'],
			                level=1)
			db.session.add(u)
			db.session.commit()
			flask_login.login_user(u)
			return flask.redirect(flask.url_for('registered'))
		except SQLException.IntegrityError as e:
			return message(message="<p>Username or email already exists</p>", url=flask.url_for('register'))


def message(message="<p>Oops - an error has occurred</p>", url="/", button="Back"):
	return flask.render_template('message.html', message=message, url=url, button=button)


@app.route('/registered')
def registered():
	return flask.render_template('message.html',
	                             message="<h4>Registration successful! </h4> <p> Make sure to check your inbox so that you can confirm your email address</p>",
	                             url=flask.url_for('console'), button="Continue")


@app.route('/chk_usrname', methods=['POST'])
def check_username():
	name = flask.request.json['name']
	if models.User.query.filter_by(username=name).first() is None:
		return dumps(True)
	else:
		return dumps(False)


@app.route('/chk_email', methods=['POST'])
def check_email():
	email = flask.request.json['email']
	if models.User.query.filter_by(email=email).first() is None:
		return dumps(True)
	else:
		return dumps(False)


@app.route('/static/css/fonts/<path:path>')
def stat(path):
	return flask.send_file('static/fonts/' + path)


@app.route('/favicons/<path:path>')
def favicons(path):
	return flask.send_file('static/images/favicons/' + path)


@app.route('/acc_register', methods=['POST'])
def acc_register():
	if flask.request.method == 'GET':
		return flask.redirect(flask.url_for('home'), code=307)
	data = loads(flask.request.json)
	user = models.User.query.filter_by(secret=data['secret']).first()
	del data['secret']
	if user is None:
		return dumps(locals.INVALID_SECRET)
	if data["email"] != "":
		m = models.Account.query.filter_by(user=user, email=data["email"]).all()
		if len(m) > 0:
			return dumps(locals.REG_ETAKEN)
	try:
		a = models.Account(user, **data)
		db.session.add(a)
		db.session.commit()
		print("Registered new user")
		return dumps(locals.SUCCESS)
	except SQLException.IntegrityError as e:
		print(e)
		return dumps(locals.REG_TAKEN)
	return dumps(locals.FAILURE)


@app.route('/acc_login', methods=['GET', 'POST'])
def check_auth():
	if flask.request.method == 'GET':
		return flask.redirect(flask.url_for('home'), code=307)

	data = loads(flask.request.json)
	account = models.Account.query.filter_by(username=data['username']).first()

	if account is not None and account.check_password(data['password']):
		return dumps(locals.SUCCESS)
	else:
		return dumps(locals.FAILURE)


@app.route('/acc_data_get', methods=['GET', 'POST'])
def acc_data_get():
	if flask.request.method == 'GET':
		return flask.redirect(flask.url_for('home'), code=307)

	data = loads(flask.request.json)
	account = models.Account.query.filter_by(username=data['username']).first()

	if account is None or not account.check_password(data['password']):
		return dumps(locals.FAILURE)
	else:
		return account.data


@app.route('/acc_data_set', methods=['GET', 'POST'])
def acc_data_set():
	if flask.request.method == 'GET':
		return flask.redirect(flask.url_for('home'), code=307)

	data = loads(flask.request.json)
	account = models.Account.query.filter_by(username=data['username']).first()

	if account is None or not account.check_password(data['password']):
		return dumps(locals.FAILURE)
	else:
		if data['overwrite']:
			account.data = dumps(data['data'])
		else:
			dic = loads(account.data)
			dic.update(data['data'])
			account.data = dumps(dic)
		db.session.commit()
		return dumps(locals.SUCCESS)


@app.before_request
def always():
	return
	print(flask.request.path)


def init():
	db.reflect()
	db.drop_all()
	db.create_all()

	"""u = models.User("bob", "mail", "123")
	db.session.add(u)

	g = models.GameServer(u, "fun", 2, 2, True, False)
	db.session.add(g)

	db.session.commit()"""
	print("Database Setup Complete")

#init()
