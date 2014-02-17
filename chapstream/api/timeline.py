import json
import logging
import calendar

import tornado.web

from chapstream import config
from chapstream.api import decorators
from chapstream.api import CsRequestHandler, process_response
from chapstream.backend.db.models.post import Post
from chapstream.backend.tasks import post_timeline
from chapstream.config import TIMELINE_CHUNK_SIZE

logger = logging.getLogger(__name__)


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