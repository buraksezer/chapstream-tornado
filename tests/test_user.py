import urllib
import logging

import mock

from chapstream.testing import CsBaseTestCase
from chapstream.backend.db.models.user import User, UserRelation
from chapstream.api import CsRequestHandler

from tests import utils

logger = logging.getLogger(__name__)


class UserRegisterTest(CsBaseTestCase):
    def test_register(self):
        data = {
            "email": "adebisi@hadronproject.org",
            "name": "adebisi",
            "password": "hadron"
        }
        data = urllib.urlencode(data)
        response = self.fetch("/register", method="POST",
                              body=data)
        self.assertEqual(response.code, 200)

        user_count = User.query.count()
        self.assertEqual(user_count, 1)

        user = User.query.filter_by(name="adebisi").first()
        self.assertNotEqual(user, None)
        self.assertEqual(user.name, "adebisi")


class UserAuth(CsBaseTestCase):
    def test_login(self):
        user = utils.create_test_user(username="foobar")
        data = {
            "name": user.name,
            "password": utils.DEFAULT_PASSWORD
        }
        data = urllib.urlencode(data)
        login_response = self.fetch("/login", method="POST",
                                    body=data,
                                    follow_redirects=False)
        # TODO: Use a better way to check authentication
        login_cookie = login_response.headers.get("Set-Cookie")
        self.assertNotEqual(login_cookie, None)

    def test_logout(self):
        user = utils.create_test_user()
        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            login_response = self.fetch("/logout", method="GET")
        self.assertEqual(login_response.code, 200)


class UserSubscription(CsBaseTestCase):
    def test_subscribe(self):
        user = utils.create_test_user()
        chap = utils.create_test_user()
        # TODO: Mock push_notification task
        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            subscribe_response = self.fetch("/api/user/subscribe/"+chap.name,
                                            body="foo",
                                            method="POST")
        res = UserRelation.query.filter_by(user_id=user.id,
                                           chap_id=chap.id).first()
        self.assertEqual(subscribe_response.code, 200)
        self.assertNotEqual(res, None)
