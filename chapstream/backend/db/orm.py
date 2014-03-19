import json

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import object_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, Text, UnicodeText

from chapstream.backend.db import chapstream_engine
from chapstream.backend.db import session


class JSONType(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None and not isinstance(value, basestring):
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class UnicodeJSONType(JSONType):
    impl = UnicodeText


class Base(object):
    # default session is scoped session
    query = session.query_property()

    @property
    def session(self):
        """Return this object's session"""
        return object_session(self)

    def __repr__(self):
        try:
            obj_id = getattr(self, 'id', None)
        except SQLAlchemyError:
            obj_id = '<SQLAlchemyError>'

        try:
            name = getattr(self, 'name', None)
        except SQLAlchemyError:
            name = None

        if isinstance(name, unicode):
            name = name.encode('utf-8', 'replace')

        cls_name = self.__class__.__name__
        if name:
            return '<%s id=%r, name=%r>' % (cls_name, obj_id, name)
        else:
            return '<%s id=%r>' % (cls_name, obj_id)

    @classmethod
    def count(cls, expr=None, _session=None):
        if _session is None:
            _session = session
        q = _session.query(func.count('*'))
        if expr is not None:
            q = q.filter(expr)
        return q.scalar() or 0

    @classmethod
    def get(cls, id):
        """Shortcut for Model.query.get()"""
        return cls.query.get(id)

    def to_dict(self, *fields):
        '''Returns model as dict. If fields is given, returns only given fields.
        If you want to change the field name in returned dict,
        give a tuple like ('real_field_name', 'wanted_field_name') instead of str.'''
        d = {}
        keys = self.__table__.columns.keys()
        if fields:
            keys = fields

        for columnName in keys:
            if isinstance(columnName, tuple):
                d[columnName[1]] = getattr(self, columnName[0])
            else:
                d[columnName] = getattr(self, columnName)
        return d

    def from_dict(self, d):
        for columnName in d.keys():
            setattr(self, columnName, d[columnName])


Base = declarative_base(bind=chapstream_engine, cls=Base)


def init_db(engine):
  """
  Creates database from models and creates indexes
  """
  Base.metadata.create_all(bind=engine)
  #engine.execute("CREATE EXTENSION pg_trgm;")
  engine.execute("CREATE INDEX user_name_trg_idx ON users USING gist (name gist_trgm_ops);")
  engine.execute("CREATE INDEX user_fullname_trg_idx ON users USING gist (fullname gist_trgm_ops);")
  engine.execute("CREATE INDEX group_name_trg_idx ON groups USING gist (name gist_trgm_ops);")