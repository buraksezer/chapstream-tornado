from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# These parameters should be defined in a config module
chapstream_engine = create_engine(
                       "postgresql://csdbuser:hadron@localhost/csdatabase",
                       convert_unicode=True,
                       echo=True # debug mode
)

session = scoped_session(sessionmaker(bind=chapstream_engine))
