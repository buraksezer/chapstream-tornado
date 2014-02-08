from chapstream.api.misc import MainHandler
from chapstream.api.user import ProfileHandler
from chapstream.api.user import LoginHandler
from chapstream.api.user import LogoutHandler
from chapstream.api.user import RegisterHandler
from chapstream.api.timeline import TimelineHandler
from chapstream.api.timeline import TimelineLoader
from chapstream.api.timeline import SendPostHandler


URLS = [
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/register", RegisterHandler),
    (r"/timeline-socket", TimelineHandler),
    (r"/send-post", SendPostHandler),
    (r"/load-timeline", TimelineLoader),
    (r"/(?P<username>[^\/]+)", ProfileHandler) # This should be at the end of the list
]
