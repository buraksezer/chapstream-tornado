import json
import logging
import calendar

import tornado.web

from chapstream import helpers
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
    def delete(self, post_rid, post_id):
        post = self.session.query(Post).filter_by(id=post_id).first()
        if not post:
            return process_response(status=config.API_FAIL,
                                    message="Post:%s could not be found."
                                            % post_id)

        # Remove the post from groups
        for group in post.groups:
            group.posts.remove(post)
        self.session.commit()

        # Remove the post from user timelines
        if post_rid:
            key = helpers.post_rid_key(post_rid)
            if self.redis_conn.hget(key, str(self.current_user.id)):
                delete_post_from_timeline(post_rid)


class TimelineLoader(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def get(self):
        """
        Simply, read user's timeline on redis. Don't hit hard drive.
        """
        timeline = helpers.user_timeline(self.current_user.id)
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


class LikeHandler(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def post(self, post_id):
        post = self.session.query(Post).filter_by(id=post_id).first()
        if not post:
            return process_response(status=config.API_FAIL,
                                    message="Post:%s could not be found."
                                            % post_id)

        if post.likes:
            post.likes.append(self.current_user.name)
        else:
            post.likes = [self.current_user.name]

        self.session.commit()

        # Set Redis data
        # TODO: Use for a helper for doing the following
        like_prefix = helpers.like_prefix(post_id)
        like_count_key= helpers.like_count_key(post_id)
        if not self.redis_conn.get(like_count_key):
            self.redis_conn.set(like_count_key, 1)
        else:
            self.redis_conn.incr(like_count_key)

        length = self.redis_conn.llen(like_prefix)
        if length == 3:
            self.redis_conn.lpop(like_prefix)

        self.redis_conn.rpush(like_prefix, self.current_user.name)

    @tornado.web.authenticated
    @decorators.api_response
    def get(self, post_id):
        post = self.session.query(Post).filter_by(id=post_id).first()
        if not post:
            return process_response(status=config.API_FAIL,
                                    message="Post:%s could not be found."
                                            % post_id)
        return process_response(data={"likes": post.likes})


    @tornado.web.authenticated
    @decorators.api_response
    def delete(self, post_id):
        post = self.session.query(Post).filter_by(id=post_id).first()
        if not post:
            return process_response(status=config.API_FAIL,
                                    message="Post:%s could not be found."
                                            % post_id)

        # TODO: Use a suitable compare method, use sqlalchemy
        if self.current_user.name in post.likes:
            # FIXME: This is an ungodly hack. Find a better way
            index = post.likes.index(self.current_user.name)
            likes = post.likes
            del likes[index]
            if not likes:
                post.likes = None
            else:
                post.likes = likes
            self.session.commit()

            # Remove from Redis
            like_prefix = helpers.like_prefix(post_id)
            # TODO: Use config module to get default values
            items = self.redis_conn.lrange(like_prefix, 0, 3)
            if self.current_user.name in items:
                like_count = helpers.like_count_key(post_id)
                self.redis_conn.lrem(like_prefix,
                                     self.current_user.name)
                self.redis_conn.decr(like_count)
        else:
            # TODO: write a suitable warning message
            return process_response(status=config.API_WARNING,
                                    message="Post:%s a warning message"
                                            % post_id)