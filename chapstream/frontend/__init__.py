import tornado
import tornado.web

from chapstream.api import CsRequestHandler

class MainHandler(CsRequestHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        name = tornado.escape.xhtml_escape(self.current_user.name)
        self.render("index.html", name=name)


class ProfileHandler(MainHandler):
    pass