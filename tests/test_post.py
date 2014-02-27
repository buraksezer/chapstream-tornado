import json
import logging

import mock
from mock import patch

from chapstream.testing import CsBaseTestCase
from chapstream.backend.db.models.group import Group
from chapstream.api import CsRequestHandler
from chapstream.backend.db import session

from chapstream.redisconn import redis_conn
from chapstream import helpers

from tests import utils


class PostTest(CsBaseTestCase):
    def test_sending_post(self):
        user = utils.create_test_user(username="lpms")
        group = utils.create_test_group(groupname="hadronproject")
        data = {
            'body': 'hey, how are you?',
        }
        data = json.dumps(data)
        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            self.fetch("/api/group/subscribe/"+str(group.id),
                       body="fooo",
                       method="POST")
            self.fetch("/api/timeline/post?receiver_groups="
                       + str(group.id),
                       body=data,
                       method="POST")

        session.rollback()
        timeline = str(user.id) + '_timeline'
        llen = redis_conn.llen(timeline)
        self.assertEqual(llen, 1)
