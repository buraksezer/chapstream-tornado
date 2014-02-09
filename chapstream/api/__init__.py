from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from chapstream.config import API_OK
from chapstream.backend.db.models.user import User


class CsRequestHandler(RequestHandler):
    """
    Base class for ChapStream request handlers
    """

    @property
    def current_user(self):
        name = self.get_secure_cookie("user")
        return self.session.query(User).filter_by(name=name).first()

    @property
    def session(self):
        return self.application.session

    @property
    def redis_conn(self):
        return self.application.redis_conn


class CsWebSocketHandler(WebSocketHandler):
    """
    Base class for ChapStream sockets
    """

    @property
    def current_user(self):
        name = self.get_secure_cookie("user")
        return self.session.query(User).filter_by(name=name).first()

    @property
    def session(self):
        return self.application.session


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

