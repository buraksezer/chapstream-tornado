import os

import tornado.web
import tornado.options
import tornado.autoreload

from chapstream.urls import URLS
from chapstream.backend.db import session
from chapstream.redisconn import redis_conn
from chapstream.config import tornado_server_settings


tornado.options.define("port", default=8000, help="Run on port", type=int)
tornado.options.define("environment", default="dev", help="environment")


class Application(tornado.web.Application):
    def __init__(self):
        debug = (tornado.options.options.environment == "dev")

        # Watch templates
        for element in ("template_path", "static_path"):
            for (path, dirs, files) in os.walk(tornado_server_settings[element]):
                for item in files:
                    tornado.autoreload.watch(os.path.join(path, item))

        tornado.web.Application.__init__(self, URLS, **tornado_server_settings)

        # global SQLAlchemy connection
        self.session = session

        # global Redis connection
        self.redis_conn = redis_conn
