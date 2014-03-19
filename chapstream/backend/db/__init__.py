from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from chapstream import config

db_url = "postgresql://%s:%s@%s/%s" % (
    config.POSTGRES_USERNAME,
    config.POSTGRES_PASSWORD,
    config.POSTGRES_HOSTNAME,
    config.POSTGRES_DATABASE
)
chapstream_engine = create_engine(
    db_url,
    convert_unicode=True,
    client_encoding="UTF8",
    echo=False # debug mode
)
session = scoped_session(sessionmaker(bind=chapstream_engine))


@contextmanager
def new_session():
    session = sessionmaker(bind=chapstream_engine)
    try:
        yield session
    finally:
        session.close()

