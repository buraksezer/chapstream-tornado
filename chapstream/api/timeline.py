import json
import logging

import tornado.web
import tornadoredis

from chapstream.api import CsRequestHandler
from chapstream.api import CsWebSocketHandler
from chapstream.backend.db import session
from chapstream.backend.db.models.post import Post
from chapstream.backend.tasks import post_timeline

logger = logging.getLogger(__name__)


class TimelineHandler(CsWebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(TimelineHandler, self).__init__(*args, **kwargs)
        self.listen()

    @tornado.web.authenticated
    @tornado.gen.engine
    def listen(self):
        logger.info('WebSocket opened.')
        self.client = tornadoredis.Client()
        self.channel = str(self.current_user.id) + '_channel'
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, self.channel)
        self.client.listen(self.on_message)

    @tornado.web.authenticated
    def on_message(self, msg):
        if msg.kind == 'message':
            logger.info('Sending a post via websocket: %s', msg.body)
            self.write_message(str(msg.body))
        if msg.kind == 'disconnect':
            logger.info('Disconnecting from channel: %s', msg.pattern)
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    @tornado.web.authenticated
    def on_close(self):
        if self.client.subscribed:
            logger.info('WebSocket closed.')
            self.client.unsubscribe(self.channel)
            self.client.disconnect()


class SendPostHandler(CsRequestHandler):
    @tornado.web.authenticated
    def post(self):
        logger.info('Creating a new post by %s', self.current_user.name)

        # Create a database record for this post on PostgreSQL database
        data = json.loads(self.request.body)
        new_post = Post(body=data["body"], user=self.current_user)
        session.add(new_post)
        session.commit()

        # Send a task to write follower's timelines and realtime push
        channel = str(self.current_user.id) + '_channel'
        post_timeline(data['body'], channel)