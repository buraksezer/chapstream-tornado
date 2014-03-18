import time
import calendar
import logging
from types import NoneType

import tornado.web

from chapstream import config
from chapstream import helpers
from chapstream.api import decorators
from chapstream.api.timeline import get_comment_summary, \
    get_post_like
from chapstream.backend.db.models.group import Group
from chapstream.api import CsRequestHandler, process_response


logger = logging.getLogger(__name__)


class GroupHandler(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def post(self):
        # TODO: Is the user a member?
        # TODO: Slugify for group name
        name = self.get_argument("name")
        if not name:
            return process_response(status=config.API_FAIL,
                                    message="You must give a group name.")
        summary = self.get_argument("summary")

        # TODO: Set some rules for group name
        # TODO: Get is_private and is_hidden
        group = Group(name=name, summary=summary)
        self.session.add(group)
        self.session.commit()

    @tornado.web.authenticated
    @decorators.api_response
    def get(self, group_id):
        group = self.session.query(Group).filter_by(id=group_id).first()
        if not group:
            result = process_response(
                message="Group:%s could not be found." % group_id,
                status=config.API_ERROR
            )
        else:
            posts = group.posts\
                .order_by("id desc")\
                .limit(config.TIMELINE_CHUNK_SIZE)\
                .all()

            length = len(posts)
            for index in xrange(0, length):
                post = posts[index]
                created_at = calendar.timegm(post.created_at.utctimetuple())
                posts[index] = {
                    "name": post.user.name,
                    "fullname": post.user.fullname,
                    "post_id": post.id,
                    "body": post.body,
                    "created_at": created_at,
                    "users_liked": get_post_like(post.id,
                                                 self.redis_conn,
                                                 self.current_user,
                                                 self.session),
                    "comments": get_comment_summary(post.id, self.redis_conn)
                }
            group_key = helpers.group_key(group_id)
            self.redis_conn.hlen(group_key)

            subscribed = False
            if self.redis_conn.sismember(
                    helpers.user_groups_key(self.current_user.id),
                    group_id):
                subscribed = True

            group_metadata = {
                "name": group.name,
                "summary": group.summary,
                "post_count": group.posts.count(),
                "subscriber_count": self.redis_conn.hlen(group_key),
                "subscribed": subscribed,
            }

            data = {
                "group": group_metadata,
                "posts": posts,
            }
            result = process_response(data=data)

        return result

    @tornado.web.authenticated
    @decorators.api_response
    def delete(self, group_id):
        group = self.session.query(Group).\
            filter_by(id=group_id).first()
        if not group:
            return process_response(status=config.API_FAIL,
                                    message="Group:%s could not be found."
                                            % group_id)

        self.session.delete(group)
        self.session.commit()


class GroupSubscriptionHandler(CsRequestHandler):
    def set_variables(self):
        self.group = helpers.group_key(self.group_id)
        self.user = str(self.current_user.id)
        self.user_groups = helpers.user_groups_key(self.user)
        self.created_at = int(time.time())

        # Check group existence
        err = self.group_existence_err
        if not isinstance(err, NoneType):
            return err

    @property
    def group_existence_err(self):
        group = self.session.query(Group).get(self.group_id)
        if not group:
            return process_response(status=config.API_FAIL,
                                    message="Group could not be found: %s"
                                            % self.group_id)
    @tornado.web.authenticated
    @decorators.api_response
    def post(self, group_id):
        self.group_id = group_id
        res = self.set_variables()
        if res is not None:
            return res

        # Check group existence
        err = self.group_existence_err
        if not isinstance(err, NoneType):
            return err

        # Add the group user's group membership list
        # Add the user to group's hash.
        if not self.redis_conn.hset(self.group, self.user, self.created_at) or \
                not self.redis_conn.sadd(self.user_groups, group_id):
            return process_response(status=config.API_FAIL,
                                    message="Subscription failed. Group: %s"
                                            % group_id)

    @tornado.web.authenticated
    @decorators.api_response
    def get(self, group_id):
        self.group_id = group_id
        res = self.set_variables()
        if res is not None:
            return res

        result = {"subscribed": False}
        if self.redis_conn.sismember(self.user_groups, group_id):
            result["subscribed"] = True
        return process_response(data=result)

    @tornado.web.authenticated
    @decorators.api_response
    def delete(self, group_id):
        self.group_id = group_id
        res = self.set_variables()
        if res is not None:
            return res

        # Add the group user's group membership list
        # Add the user to group's hash.
        if not self.redis_conn.hdel(self.group, self.user) or \
                not self.redis_conn.srem(self.user_groups, group_id):
            return process_response(status=config.API_FAIL,
                                    message="Subscription removing failed. Group: %s"
                                            % group_id)
