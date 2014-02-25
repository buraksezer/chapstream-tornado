import time
import logging
from types import NoneType

import tornado.web

from chapstream import config
from chapstream import helpers
from chapstream.api import decorators
from chapstream.backend.db.models.post import Post
from chapstream.backend.db.models.group import Group
from chapstream.api import CsRequestHandler, process_response


logger = logging.getLogger(__name__)


class GroupHandler(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def post(self):
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

        return process_response(status=config.API_OK)

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
        return process_response(status=config.API_OK)


class GroupSubscriptionHandler(CsRequestHandler):
    def set_variables(self):
        self.group = helpers.group_key(self.group_id)
        self.user = str(self.current_user.id)
        self.user_groups = helpers.user_groups_key(self.user)
        self.created_at = int(time.time())

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
        self.set_variables()

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

        return process_response(status=config.API_OK)

    @tornado.web.authenticated
    @decorators.api_response
    def delete(self, group_id):
        self.group_id = group_id
        self.set_variables()

        # Check group existence
        err = self.group_existence_err
        if not isinstance(err, NoneType):
            return err

        # Add the group user's group membership list
        # Add the user to group's hash.
        if not self.redis_conn.hdel(self.group, self.user) or \
                not self.redis_conn.srem(self.user_groups, group_id):
            return process_response(status=config.API_FAIL,
                                    message="Subscription removing failed. Group: %s"
                                            % group_id)

        return process_response(status=config.API_OK)