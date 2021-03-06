from tornado.testing import AsyncHTTPTestCase


from chapstream.backend.db.orm import Base
from chapstream.backend.db import session
from chapstream.redisconn import redis_conn
from chapstream.app import Application


def truncate_tables():
    session.rollback()
    tables = Base.metadata.tables.values()
    tables.reverse()
    for table in tables:
        session.execute(table.delete())


def flushdb_redis():
    return redis_conn.flushdb()


class CsBaseTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def setUp(self):
        # Truncate all of the tables
        flushdb_redis()
        truncate_tables()
        super(CsBaseTestCase, self).setUp()
