import urllib
import logging

import mock

from chapstream.testing import CsBaseTestCase
from chapstream.backend.db.models.group import Group
from chapstream.api import CsRequestHandler
from chapstream.redisconn import redis_conn
from chapstream import helpers

from tests import utils

logger = logging.getLogger(__name__)


class GroupTest(CsBaseTestCase):
    def test_group_create(self):
        user = utils.create_test_user(username="hadron")
        data = {
            "name": "hadronproject",
            "summary": "the best source based gnu/linux distro"
        }
        data = urllib.urlencode(data)

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            response = self.fetch("/api/group",
                                  body=data,
                                  method="POST")

        group = Group.query.first()
        self.assertEqual(response.code, 200)
        self.assertNotEqual(group, None)
        self.assertEqual(group.name, "hadronproject")

    def test_group_delete(self):
        user = utils.create_test_user(username="lpms")
        group = utils.create_test_group(groupname="gr1")

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            response = self.fetch("/api/group/"+str(group.id),
                                  method="DELETE")

        self.assertEqual(response.code, 200)

        check = Group.query.filter_by(name="foobargroup").first()
        self.assertEqual(check, None)

    def test_group_subs_unsubs(self):
        user = utils.create_test_user(username="emmett_brown")
        group = utils.create_test_group(groupname="back_to_the_future")

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            subs_response = self.fetch("/api/group/subscribe/"+str(group.id),
                                       body="fooo",
                                       method="POST")

        self.assertEqual(subs_response.code, 200)

        # Redis checks
        group_key = helpers.group_key(group.id)
        user_groups = helpers.user_groups_key(user.id)

        # expect a UNIX epoch instead of None
        subs_membership = redis_conn.hget(group_key,
                                          str(user.id))
        self.assertNotEqual(subs_membership, None)

        # reverse membership
        subs_reverse_membership = redis_conn.sismember(user_groups,
                                                       str(group.id))
        self.assertEqual(subs_reverse_membership, True)

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            unsubs_response = self.fetch("/api/group/subscribe/"+str(group.id),
                                         method="DELETE")

        self.assertEqual(unsubs_response.code, 200)

        # Redis checks
        unsubs_membership = redis_conn.hget(group_key, str(user.id))
        self.assertEqual(unsubs_membership, None)

        # reverse membership
        unsubs_reverse_membership = redis_conn.sismember(user_groups,
                                                         str(group.id))
        self.assertEqual(unsubs_reverse_membership, False)
