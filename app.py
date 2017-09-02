#!/usr/bin/env python
# coding:utf-8
import sys
import os
import logging
import shlex
import gunicorn.app.wsgiapp

host = '0.0.0.0'
port = '8080'

# This line
cmd = 'gunicorn -b %s:%d -k "flask_sockets.worker" flaskapp:app' % (host, int(port))
sys.argv = shlex.split(cmd)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%b %d %H:%M:%S]')
os.chdir(os.path.abspath(os.path.dirname(__file__)))
gunicorn.app.wsgiapp.run()