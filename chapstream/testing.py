from tornado.testing import AsyncHTTPTestCase

from sqlalchemy import MetaData

from chapstream.backend.db.orm import Base
from chapstream.backend.db import session
from chapstream.app import Application


def truncate_tables():
    for table in Base.metadata.tables.values():
        session.execute(table.delete())


class CsBaseTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def setUp(self):
        # Truncate all of the tables
        truncate_tables()
        super(CsBaseTestCase, self).setUp()
