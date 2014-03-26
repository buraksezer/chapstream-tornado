import os
import json
import logging
import calendar

import tornado.web

from chapstream import helpers
from chapstream import config
from chapstream.api import decorators
from chapstream.api import CsRequestHandler, process_response
from chapstream.api.comment import get_comment_summary
from chapstream.backend.db.models.post import Post
from chapstream.backend.db.models.user import User
from chapstream.backend.db.models.group import Group
from chapstream.backend.tasks import post_timeline, \
    delete_post_from_timeline, push_like
from chapstream.config import TIMELINE_CHUNK_SIZE

logger = logging.getLogger(__name__)


class PostHandler(CsRequestHandler):
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
        # receiver_users argument contains user names that are seperated with comma
        receiver_users = self.get_argument("receiver_users", None)
        mystream = self.get_argument("mystream")
        if receiver_users:
            receiver_users = [user for user in receiver_users.split(",")]

        receiver_groups = self.get_argument("receiver_groups", None)
        # TODO: Check subscription status
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

        if mystream == 0:
            post_timeline(post, receiver_groups=receiver_groups)
            # TODO: push_notification_about_mention_for_receiver_users
        else:
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
            post = json.loads(post)
            # Aggregate like votes
            users_liked = get_post_like(post["post_id"],
                                        self.redis_conn,
                                        self.current_user,
                                        self.session)
            post["users_liked"] = users_liked

            # Aggregate comments
            comments = get_comment_summary(post["post_id"], self.redis_conn)
            post["comments"] = comments

            posts[index] = post
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

        # Set Redis data
        userlike_key = helpers.userlike_key(self.current_user.id)
        postlike_key = helpers.postlike_key(post_id)
        if not self.redis_conn.sismember(userlike_key, post_id):
            self.redis_conn.sadd(userlike_key, post_id)
            self.redis_conn.rpush(postlike_key, self.current_user.name)
        else:
            return process_response(status=config.API_WARNING,
                                    message="You have already liked Post:%s"
                                            % post_id)
        push_like(post_id, self.current_user.id)


    @tornado.web.authenticated
    @decorators.api_response
    def get(self, post_id):
        post = self.session.query(Post).filter_by(id=post_id).first()
        if not post:
            return process_response(status=config.API_FAIL,
                                    message="Post:%s could not be found."
                                            % post_id)
        path = os.path.basename(self.request.path)
        result = get_post_like(post_id, self.redis_conn,
                               self.current_user, self.session,
                               path=path)
        return process_response(result)

    @tornado.web.authenticated
    @decorators.api_response
    def delete(self, post_id):
        post = self.session.query(Post).filter_by(id=post_id).first()
        if not post:
            return process_response(status=config.API_FAIL,
                                    message="Post:%s could not be found."
                                            % post_id)

        userlike_key = helpers.userlike_key(self.current_user.id)
        postlike_key = helpers.postlike_key(post_id)
        if not self.redis_conn.sismember(userlike_key, post_id):
            return process_response(status=config.API_FAIL,
                                    message="You have no like vote for Post:%s"
                                            % post_id)
        self.redis_conn.srem(userlike_key, post_id)
        self.redis_conn.lrem(postlike_key, self.current_user.name)


def get_post_like(post_id, redis_conn, current_user, session, path=None):
    """
    Gets 'like' data for loading timeline from Redis cluster.
    """
    userlike_key = helpers.userlike_key(current_user.id)
    postlike_key = helpers.postlike_key(post_id)
    liked = redis_conn.sismember(userlike_key, post_id)
    length = redis_conn.llen(postlike_key)
    if path == "all":
        result = {"users": redis_conn.lrange(postlike_key, 0, length)}
    else:
        # Get last 3 items
        min_ = 0 if length < 3 else length - 3
        last_likes = redis_conn.lrange(postlike_key, min_, length)
        users = []
        for item in last_likes:
            #TODO:  Create an index for user names
            user = session.query(User).filter_by(name=item).first()
            if user == current_user:
                screen_name = "You"
            else:
                screen_name = user.fullname if user.fullname else user.name

            users.append(
                {
                    "name": item,
                    "screen_name": screen_name  ,
                }
            )
        result = {"users": users}

    result["liked"] = liked
    result["count"] = length
    return result