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
    def get_current_user(self):
        return self.get_secure_cookie("user")
