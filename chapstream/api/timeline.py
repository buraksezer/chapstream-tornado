import json
import logging
import calendar

import tornado.web

from chapstream import config
from chapstream.api import decorators
from chapstream.api import CsRequestHandler, process_response
from chapstream.backend.db.models.post import Post
from chapstream.backend.db.models.group import Group
from chapstream.backend.tasks import post_timeline, \
    delete_post_from_timeline
from chapstream.config import TIMELINE_CHUNK_SIZE

logger = logging.getLogger(__name__)


class PostHandler(CsRequestHandler):
    @tornado.web.authenticated
    def post(self):
        logger.info('Creating a new post by %s', self.current_user.name)

        # Create a database record for this post on PostgreSQL database
        data = json.loads(self.request.body)
        body = data["body"].decode('UTF-8')
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
        # receiver_users argument contains user names that are seperated with comma
        receiver_users = self.get_argument("receiver_users", None)
        if receiver_users:
            receiver_users = [user for user in receiver_users.split(",")]

        receiver_groups = self.get_argument("receiver_groups", None)
        if receiver_groups:
            receiver_groups = [group for group in receiver_groups.split(",")]
            # Add posts to the group on PostgreSQL
            for index in xrange(0, len(receiver_groups)):
                group_id = receiver_groups[index]
                group = self.session.query(Group).filter_by(
                    id=group_id).first()
                if not group:
                    logger.warning("Invalid Group:%s" % group_id)
                    del receiver_groups[index]
                    continue
                # Add the post to the group
                group.posts.append(new_post)

            # Send all changes in a transaction
            self.session.commit()

        post_timeline(post, receiver_users=receiver_users,
                      receiver_groups=receiver_groups)

    @tornado.web.authenticated
    @decorators.api_response
    def delete(self):
        post_rid = self.get_argument("post_rid")
        post_id = self.get_argument("post_id")
        post = self.session.query(Post).filter_by(id=post_id).first()
        if not post:
            return process_response(status=config.API_OK,
                                    message="Post:%s could not be found."
                                            % post_id)

        # Remove the post from groups
        for group in post.groups:
            group.posts.remove(post)
        self.session.commit()

        # Remove the post from user timelines
        if post_rid:
            key = "post_rid::" + post_rid
            if self.redis_conn.hget(key, str(self.current_user.id)):
                delete_post_from_timeline(post_rid)


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
        return process_response(data=posts)
