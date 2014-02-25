import urllib
import logging

from chapstream.testing import CsBaseTestCase
from chapstream.backend.db.models.group import Group
from chapstream.api import CsRequestHandler
from chapstream.backend.db import session

from tests import utils

logger = logging.getLogger(__name__)


class GroupTest(CsBaseTestCase):
    def test_group_create(self):
        user = utils.create_test_user(username="hadron")
        group_name = "hadronproject"
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
        group = Group(name="foobargroup")
        session.add(group)
        session.commit()

        with mock.patch.object(CsRequestHandler,
                               "get_secure_cookie") as m:
            m.return_value = user.name
            response = self.fetch("/api/group/"+str(group.id),
                                  method="DELETE")

        self.assertEqual(response.code, 200)

        check = Group.query.filter_by(name="foobargroup").first()
        self.assertEqual(check, None)