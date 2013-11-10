from tornado.web import RequestHandler


class CsRequestHandler(RequestHandler):
    """
    Base class for ChapStream request handlers
    """
    def get_current_user(self):
        return self.get_secure_cookie("user")