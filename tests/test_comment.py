import json
import logging

import mock

from chapstream.testing import CsBaseTestCase
from chapstream.backend.db.models.comment import Comment
from chapstream.api import CsRequestHandler
from chapstream.redisconn import redis_conn
from chapstream import helpers
from chapstream import config

from tests import utils

logger = logging.getLogger(__name__)


class CommentTest(CsBaseTestCase):
    def test_comment(self):
        user1 = utils.create_test_user()
        user2 = utils.create_test_user()
        post = utils.create_test_post(user1.id)

        data = {
            'body': 'hey, how are you?',
        }
        data = json.dumps(data)

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user2.name
            send_response = self.fetch("/api/comment/%s" % post.id,
                                       body=data,
                                       method="POST")

        userintr_hash = "userintr:" + str(user2.id)
        userintr_res = redis_conn.hget(userintr_hash, str(post.id))
        self.assertNotEqual(userintr_res, None)

        comment_summary = "cs::" + str(post.id)
        self.assertEqual(redis_conn.llen(comment_summary), 1)

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user2.name
            get_response = self.fetch("/api/comment/%s" % post.id,
                                       method="GET")

        g_json = json.loads(get_response.body)
        logger.info(g_json)
        self.assertEqual(len(g_json["comments"]), 1)

        s_json = json.loads(send_response.body)
        comment_id = s_json["comment"]["id"]

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user2.name
            self.fetch("/api/comment-delete/%s" % comment_id,
                       method="DELETE")

        self.assertEqual(Comment.get(comment_id), None)
        userintr_res = redis_conn.hget(userintr_hash, str(post.id))
        self.assertEqual(userintr_res, None)
        self.assertEqual(redis_conn.llen(comment_summary), 0)
