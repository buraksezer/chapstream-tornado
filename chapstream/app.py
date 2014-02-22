import os

import tornado.web
import tornado.options
import tornado.autoreload

from chapstream.urls import URLS
from chapstream.backend.db import session
from chapstream.redisconn import redis_conn
from chapstream.config import tornado_server_settings, \
    POST_RID, POST_RID_HEAD_KEY


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

        # Global SQLAlchemy connection
        self.session = session

        # Global Redis connection
        self.redis_conn = redis_conn

        # Set POST_RID_HEAD_KEY if not set
        if not self.redis_conn.get(POST_RID_HEAD_KEY):
            self.redis_conn.set(POST_RID_HEAD_KEY, POST_RID)
