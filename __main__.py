from app import app

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from werkzeug.serving import run_with_reloader
from werkzeug.debug import DebuggedApplication

from gevent import monkey
monkey.patch_all()

def run_server():
    if app.debug:
        application = DebuggedApplication(app)
    else:
        application = app

    server = pywsgi.WSGIServer(('127.0.0.1', 8000), application,
                               handler_class=WebSocketHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_with_reloader(run_server)