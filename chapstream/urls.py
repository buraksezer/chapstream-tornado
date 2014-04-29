# Frontend Handlers
from chapstream.frontend import MainHandler
from chapstream.frontend import DummyHandler

# API Handlers
# User related handlers
from chapstream.api.user import UserHandler
from chapstream.api.user import BlockHandler
from chapstream.api.user import LoginHandler
from chapstream.api.user import LogoutHandler
from chapstream.api.user import RegisterHandler
from chapstream.api.user import SubscriptionHandler
from chapstream.api.user import RelationshipStatusHandler
from chapstream.api.user import LikedPostsHandler
from chapstream.api.search import PostReceivers

# Timeline related handlers
from chapstream.api.commons import RealtimeHandler
from chapstream.api.timeline import TimelineLoader
from chapstream.api.timeline import PostHandler
from chapstream.api.timeline import LikeHandler
from chapstream.api.comment import CollectCommentsHandler
from chapstream.api.comment import CommentHandler

# Group related handlers
from chapstream.api.group import GroupSubscriptionHandler
from chapstream.api.group import GroupHandler


FRONTEND_URLS = [
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/register", RegisterHandler),
    (r"/group/(?P<group_id>[^\/]+)", DummyHandler),
    (r"/(?P<username>[^\/]+)", DummyHandler) # This should be at the end of the list
]

API_URLS = [
    (r"/api/search/postreceivers/(?P<query>[^\/]+)", PostReceivers),
    (r"/api/comment/(?P<post_id>[^\/]+)", CommentHandler),
    (r"/api/comment/(?P<post_id>[^\/]+)/all", CommentHandler),
    (r"/api/comment-delete/(?P<comment_id>[^\/]+)", CommentHandler),
    (r"/api/comment-update/(?P<comment_id>[^\/]+)", CommentHandler),
    (r"/api/like/(?P<post_id>[^\/]+)/all", LikeHandler),
    (r"/api/like/(?P<post_id>[^\/]+)", LikeHandler),
    (r"/api/group/subscribe/(?P<group_id>[^\/]+)", GroupSubscriptionHandler),
    (r"/api/group", GroupHandler),
    (r"/api/group/(?P<group_id>[^\/]+)", GroupHandler),
    (r"/api/timeline/load-timeline", TimelineLoader),
    (r"/api/timeline/post", PostHandler),  # Post sending
    (r"/api/timeline/post/(?P<post_rid>[^\/]+)/(?P<post_id>[^\/]+)", PostHandler),  # Delete
    (r"/api/user/relationship/(?P<username>[^\/]+)", RelationshipStatusHandler),
    (r"/api/user/subscribe/(?P<username>[^\/]+)", SubscriptionHandler),
    (r"/api/user/unsubscribe/(?P<username>[^\/]+)", SubscriptionHandler),
    (r"/api/user/block/(?P<username>[^\/]+)", BlockHandler),
    (r"/api/user/unblock/(?P<username>[^\/]+)", BlockHandler),
    (r"/api/user/likedposts", LikedPostsHandler),
    (r"/api/user/comments", CollectCommentsHandler),
    (r"/api/user/(?P<username>[^\/]+)", UserHandler),  # This should be at the end of the list
]

MISC_URLS = [
    (r"/timeline-socket", RealtimeHandler),
]

URLS = API_URLS + MISC_URLS +FRONTEND_URLS