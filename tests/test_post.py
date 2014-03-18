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

        timeline = helpers.user_timeline(user.id)
        llen = redis_conn.llen(timeline)
        self.assertEqual(llen, 1)

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            timeline = self.fetch("/api/timeline/load-timeline",
                                  method="GET")

        body = json.loads(timeline.body)
        post = body['posts'][0]
        post_rid = post["rid"]
        post_id = post["post_id"]
        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            self.fetch("/api/timeline/post/%s/%s" %
                       (post_rid, post_id),
                       method="DELETE")

        timeline = helpers.user_timeline(user.id)
        llen = redis_conn.llen(timeline)
        self.assertEqual(llen, 0)


class LikeTest(CsBaseTestCase):
    def test_like(self):
        user = utils.create_test_user(username="lpms")
        body = "foobarpost".decode('UTF-8')
        post = Post(body=body, user_id=user.id)
        session.add(post)
        session.commit()

        userlike_key = helpers.userlike_key(user.id)
        postlike_key = helpers.postlike_key(post.id)

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            self.fetch("/api/like/%s" % post.id, body="foo",
                       method="POST")

            get_response = self.fetch("/api/like/%s"
                                      % post.id, method="GET")

        result = json.loads(get_response.body)
        logging.info(result)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["liked"], True)
        for user_liked in result["users"]:
            self.assertEqual(user.name, user_liked["name"])

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            self.fetch("/api/like/%s" % post.id, method="DELETE")
            self.fetch("/api/like/%s"
                       % post.id, method="GET")

        s_ismember = redis_conn.sismember(userlike_key, post.id)
        self.assertEqual(s_ismember, False)
        self.assertEqual(redis_conn.llen(postlike_key), 0)
