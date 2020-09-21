from flask import Flask, redirect, url_for, render_template, \
    request, make_response, Response, Markup, g
from flask_socketio import SocketIO, send, emit, join_room, leave_room

try:
    from waitress import serve
except ImportError:
    serve = None

import os
import logging

from wrapper.dashboard.login import blueprint_login
from wrapper.dashboard.admin import blueprint_admin
from wrapper.dashboard.auth import Auth
from wrapper.dashboard.events import Events

class Dashboard:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.config = wrapper.config["dashboard"]
        self.log = wrapper.log_manager.get_logger("dashboard")

        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.urandom(32)
        self.app.config['TEMPLATES_AUTO_RELOAD'] = True

        # Only log crucial errors
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        self.app.wrapper = self.wrapper

        self.socketio = SocketIO(self.app, async_mode="threading")

        self.auth = Auth(self.wrapper)

        self.ioevents = Events(self.wrapper, self.socketio, self.auth)
        self.socketio.on_namespace(self.ioevents)

        self.do_decorators()
        self.register_blueprints()

    def do_decorators(self):
        # https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
        def human_bytes(num, suffix="B"):
            for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
                if abs(num) < 1024.0:
                    return "%3.1f%s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.1f%s%s" % (num, "Yi", suffix)
        self.app.jinja_env.filters["human_bytes"] = human_bytes

    def register_blueprints(self):
        self.app.register_blueprint(blueprint_login)
        self.app.register_blueprint(blueprint_admin)

    def run(self):
        if serve:
            serve(
                self.app,
                host=self.config["bind"]["ip"],
                port=self.config["bind"]["port"],
                threads=32
            )
        else:
            self.socketio.run(
                self.app,
                host=self.config["bind"]["ip"],
                port=self.config["bind"]["port"],
                debug=self.wrapper.debug,
                use_reloader=False
            )
