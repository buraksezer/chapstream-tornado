import urllib
import logging

from chapstream.testing import CsBaseTestCase
from chapstream.backend.db.models.user import User

logger = logging.getLogger(__name__)


class UserAuthTest(CsBaseTestCase):
    def test_register(self):
        data = {
            "email": "adebisi@chapstream.com",
            "name": "adebisi",
            "password": "hadron"
        }
        data = urllib.urlencode(data)
        logger.info(data)
        response = self.fetch("/register", method="POST", body=data)
        self.assertEqual(response.code, 200)

        user_count = User.query.count()
        self.assertEqual(user_count, 1)

        user = User.query.filter_by(name="adebisi").first()
        self.assertNotEqual(user, None)
        self.assertEqual(user.name, "adebisi")




