from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from chapstream.config import API_OK
from chapstream.backend.db import session
from chapstream.backend.db.models.user import User


class CsRequestHandler(RequestHandler):
    """
    Base class for ChapStream request handlers
    """

    @property
    def current_user(self):
        name = self.get_secure_cookie("user")
        return session.query(User).filter_by(name=name).first()


class CsWebSocketHandler(WebSocketHandler):
    """
    Base class for ChapStream sockets
    """

    @property
    def current_user(self):
        name = self.get_secure_cookie("user")
        return session.query(User).filter_by(name=name).first()


def process_response(data=None, status=API_OK, message=None):
    """
    Process API responses and creates a boilerplate dict.
    """
    scheme = {"status": status}
    if status != API_OK:
        scheme['message'] = message
    else:
        scheme.update(data)

    return scheme

