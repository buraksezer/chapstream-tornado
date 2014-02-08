from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import object_session
from sqlalchemy.ext.declarative import declarative_base

from chapstream.backend.db import chapstream_engine
from chapstream.backend.db import session


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
  Base.metadata.create_all(bind=engine)