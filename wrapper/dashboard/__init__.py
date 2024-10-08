from flask import Flask
from flask_socketio import SocketIO

try:
    from waitress import serve
except ImportError:
    serve = None

import os
import logging
import datetime as dt
import humanize

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
            if not num:
                return "null"

            for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
                if abs(num) < 1024.0:
                    return "%3.1f%s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.1f%s%s" % (num, "Yi", suffix)
        self.app.jinja_env.filters["human_bytes"] = human_bytes

        def naturaldelta(seconds):
            delta = dt.timedelta(seconds=seconds)

            return humanize.naturaldelta(delta)

        self.app.jinja_env.filters["naturaldelta"] = naturaldelta

        def naturaltime(seconds):
            delta = dt.datetime.fromtimestamp(seconds)

            return humanize.naturaltime(delta)

        self.app.jinja_env.filters["naturaltime"] = naturaltime

        def pretty_timestamp(seconds):
            d = dt.datetime.fromtimestamp(seconds)

            return d.strftime("%Y/%m/%d %I:%M:%S%p")

        self.app.jinja_env.filters["pretty_timestamp"] = pretty_timestamp

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
