from gevent import monkey
monkey.patch_all()
from app import app

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from werkzeug.serving import run_with_reloader
from werkzeug.debug import DebuggedApplication
from os import path
import os


def run_server():
	application = DebuggedApplication(app)

	server = pywsgi.WSGIServer(('127.0.0.1', 8000), application,
							   handler_class=WebSocketHandler)
	server.serve_forever()

if __name__ == "__main__":
	extra_dirs = ['templates', ]
	extra_files = extra_dirs[:]
	for extra_dir in extra_dirs:
		for dirname, dirs, files in os.walk(extra_dir):
			for filename in files:
				filename = path.join(dirname, filename)
				if path.isfile(filename):
					extra_files.append(filename)
	run_with_reloader(run_server, extra_files=extra_files)
	#run_server()