# Frontend Handlers
from chapstream.frontend import MainHandler
from chapstream.frontend import ProfileHandler

# API Handlers
# User related handlers
from chapstream.api.user import UserHandler
from chapstream.api.user import LoginHandler
from chapstream.api.user import LogoutHandler
from chapstream.api.user import RegisterHandler
from chapstream.api.user import RelationshipStatusHandler
from chapstream.api.user import SubscriptionHandler
from chapstream.api.user import BlockHandler

# Timeline related handlers
from chapstream.api.timeline import TimelineHandler
from chapstream.api.timeline import TimelineLoader
from chapstream.api.timeline import SendPostHandler

FRONTEND_URLS = [
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/register", RegisterHandler),
    (r"/(?P<username>[^\/]+)", ProfileHandler) # This should be at the end of the list
]

API_URLS = [
    (r"/api/timeline/load-timeline", TimelineLoader),
    (r"/api/timeline/send-post", SendPostHandler),
    (r"/api/user/(?P<username>[^\/]+)", UserHandler),  # This should be at the end of the list
    (r"/api/user/relationship/(?P<username>[^\/]+)", RelationshipStatusHandler),
    (r"/api/user/subscribe/(?P<username>[^\/]+)", SubscriptionHandler),
    (r"/api/user/unsubscribe/(?P<username>[^\/]+)", SubscriptionHandler),
    (r"/api/user/block/(?P<username>[^\/]+)", BlockHandler),
    (r"/api/user/unblock/(?P<username>[^\/]+)", BlockHandler),
]

MISC_URLS = [
    (r"/timeline-socket", TimelineHandler),
]

URLS = API_URLS + MISC_URLS +FRONTEND_URLS