import tornadoredis
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

class CsRequestHandler(RequestHandler):
    """
    Base class for ChapStream request handlers
    """
    def get_current_user(self):
        return self.get_secure_cookie("user")


class CsWebSocketHandler(WebSocketHandler):
    """
    Base class for ChapStream sockets
    """
    def redis_conn(self):
        conn = tornadoredis.Client()
        return conn.connect()

    def get_current_user(self):
        return self.get_secure_cookie("user")
