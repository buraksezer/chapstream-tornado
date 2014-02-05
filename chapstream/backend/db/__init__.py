from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# These parameters should be defined in a config module
chapstream_engine = create_engine(
                       "postgresql://csdbuser:hadron@localhost/csdatabase",
                       convert_unicode=True,
                       client_encoding="UTF8",
                       echo=False # debug mode
)
session = scoped_session(sessionmaker(bind=chapstream_engine))
Base = declarative_base()

def init_db(engine):
  Base.metadata.create_all(bind=engine)