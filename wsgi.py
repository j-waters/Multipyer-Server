#!/usr/bin/env python
# coding:utf-8
"""import sys
import os
import logging
import shlex
import gunicorn.app.wsgiapp

host = os.environ.get('OPENSHIFT_DIY_IP', '127.0.0.1')
port = os.environ.get('OPENSHIFT_DIY_PORT', '8080')

# This line
cmd = 'gunicorn -b %s:%d -k "flask_sockets.worker" app:app' % (host, int(port))
sys.argv = shlex.split(cmd)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%b %d %H:%M:%S]')
os.chdir(os.path.abspath(os.path.dirname(__file__)))
gunicorn.app.wsgiapp.run()"""
#from app import app as application

from flask import Flask
application = Flask(__name__)

@application.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
	print("main")
    application.run()
