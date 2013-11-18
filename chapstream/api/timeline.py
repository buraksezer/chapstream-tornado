import json

import tornado.web

from chapstream.api import CsRequestHandler
from chapstream.api import CsWebSocketHandler
from chapstream.backend.db import session
from chapstream.backend.db.models.user import User
from chapstream.backend.db.models.post import Post


class TimelineHandler(CsWebSocketHandler):
    @tornado.web.authenticated
    def open(self):
        print "websocket opened"

    @tornado.web.authenticated
    def on_message(self, message):
        channel = self.current_user+"_timeline"
        self.redis_conn(channel, message)
        #self.write_message(u"you said: "+ message)

    @tornado.web.authenticated
    def on_close(self):
        print "websocket closed"


class SendPostHandler(CsRequestHandler):
    @tornado.web.authenticated
    def post(self):
        # TODO: Catch exceptions
        data = json.loads(self.request.body)
        user = session.query(User).filter_by(name=self.current_user).first()
        new_post = Post(body=data["body"], user_id=user.id)
        session.add(new_post)
        session.commit()
