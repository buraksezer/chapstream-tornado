import json
import logging

import mock
from mock import patch

from chapstream.testing import CsBaseTestCase
from chapstream.backend.db.models.group import Group
from chapstream.api import CsRequestHandler
from chapstream.backend.db import session
from chapstream.backend.db.models.post import Post

from chapstream.redisconn import redis_conn
from chapstream import helpers

from tests import utils


class PostTest(CsBaseTestCase):
    def test_post(self):
        user = utils.create_test_user(username="lpms")
        group = utils.create_test_group(groupname="hadronproject")
        data = {
            'body': 'hey, how are you?',
        }
        data = json.dumps(data)

        # Sending post
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

        timeline = str(user.id) + '_timeline'
        llen = redis_conn.llen(timeline)
        self.assertEqual(llen, 1)

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            timeline = self.fetch("/api/timeline/load-timeline",
                                  method="GET")

        body = json.loads(timeline.body)
        # TODO: rename id_ to rid
        post = body['posts'][0]
        post_rid = post["id_"]
        post_id = post["post_id"]
        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            self.fetch("/api/timeline/post/%s/%s" %
                       (post_rid, post_id),
                       method="DELETE")

        timeline = str(user.id) + '_timeline'
        llen = redis_conn.llen(timeline)
        self.assertEqual(llen, 0)


class LikeTest(CsBaseTestCase):
    def test_like(self):
        user = utils.create_test_user(username="lpms")
        body = "foobarpost".decode('UTF-8')
        post = Post(body=body, user_id=user.id)
        session.add(post)
        session.commit()

        like_prefix = "like::"+str(post.id)
        like_count = "like_count::"+str(post.id)

        def check(result, count, bool_):
            self.assertEqual(redis_conn.llen(like_prefix), count)
            c = int(redis_conn.get(like_count))
            self.assertEqual(c, count)

            result = json.loads(result)
            ul = False
            if result["likes"]:
                ul = user.name in result["likes"]

            self.assertEqual(ul, bool_)

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            self.fetch("/api/like/%s" % post.id, body="foo",
                       method="POST")

            get_response = self.fetch("/api/like/%s"
                                      % post.id, method="GET")

        check(get_response.body, 1, True)

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            self.fetch("/api/like/%s" % post.id, method="DELETE")
            get_response = self.fetch("/api/like/%s"
                                      % post.id, method="GET")

        check(get_response.body, 0, False)
