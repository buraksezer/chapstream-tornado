import json
import logging
import calendar

import tornado.web
import tornadoredis

from chapstream import config
from chapstream.api import decorators
from chapstream.api import CsRequestHandler, process_response
from chapstream.api import CsWebSocketHandler
from chapstream.backend.db.models.user import UserRelation
from chapstream.backend.db.models.post import Post
from chapstream.backend.tasks import post_timeline
from chapstream.config import TIMELINE_CHUNK_SIZE

logger = logging.getLogger(__name__)


class TimelineHandler(CsWebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(TimelineHandler, self).__init__(*args, **kwargs)
        self.listen()

    @tornado.web.authenticated
    @tornado.gen.engine
    def listen(self):
        logger.info('WebSocket opened.')
        self.client = tornadoredis.Client(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT
        )
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
        body = data["body"].encode('UTF-8')
        new_post = Post(body=body, user=self.current_user)
        self.session.add(new_post)
        self.session.commit()

        # Send a task to write follower's timelines and realtime push
        created_at = calendar.timegm(new_post.created_at.utctimetuple())
        post = {
            'post_id': new_post.id,
            'body': body,
            'created_at': created_at,
            'user_id': self.current_user.id,
            'name': self.current_user.name,
            'fullname': self.current_user.fullname
        }
        post_timeline(post)


class TimelineLoader(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def get(self):
        """
        Simply, read user's timeline on redis. Don't hit hard drive.
        """
        timeline = str(self.current_user.id) + '_timeline'
        length = self.redis_conn.llen(timeline)
        offset = length - TIMELINE_CHUNK_SIZE
        posts = self.redis_conn.lrange(timeline, offset, length)
        posts.reverse()

        # We process all items of the list because
        # redis returns a raw string instead of a python object.
        for index in xrange(0, len(posts)):
            post = posts[index]
            posts[index] = json.loads(post)
        posts = {"posts": posts}
        result = process_response(data=posts, status=config.API_OK)

        return result