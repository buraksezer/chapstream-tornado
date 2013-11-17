import tornado.web

from chapstream.api import CsRequestHandler
from chapstream.api import CsWebSocketHandler


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
        print "burda"