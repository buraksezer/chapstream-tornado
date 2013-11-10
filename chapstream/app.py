from tornado.web import Application
from chapstream.config import settings

from chapstream.api.misc import MainHandler
from chapstream.api.user import ProfileHandler
from chapstream.api.user import LoginHandler
from chapstream.api.user import LogoutHandler
from chapstream.api.user import RegisterHandler



application = Application([
    (r"/", MainHandler),
    (r"/profile", ProfileHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/register", RegisterHandler)
], **settings)
