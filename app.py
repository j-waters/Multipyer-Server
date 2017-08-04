from flask import Flask
from flask_sockets import Sockets
import gevent
import time
from server import Server
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.debug = True
sockets = Sockets(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('OPENSHIFT_POSTGRESQL_DB_URL', '127.11.222.130:5432')
#db = SQLAlchemy(app)
#db.create_all()

svr = Server()


@sockets.route('/connect')
def connect(ws):
	svr.connect(ws)
	while True:
		gevent.sleep(0)


@app.route('/')
def test():
	print(app.config['SQLALCHEMY_DATABASE_URI'])
	return "All is well"