import hashlib
from datetime import datetime

from sqlalchemy import Column, Integer,\
    String, DateTime, Boolean, UnicodeText, Sequence, \
    BigInteger
from sqlalchemy.orm import relationship

from chapstream.backend.db.orm import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, Sequence(
        'seq_user_id', start=1, increment=1), primary_key=True)
    name = Column(String, nullable=False)
    fullname = Column(String)
    email = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    # TODO: rename this: is_private
    is_hidden = Column(Boolean, default=False)
    bio = Column(UnicodeText, nullable=True)
    sign_up_date = Column(DateTime, default=datetime.utcnow())
    last_seen = Column(DateTime, default=datetime.utcnow())
    posts = relationship('Post', backref='user', lazy='dynamic')
    notifications = relationship('Notification', backref='user', lazy='dynamic')

    def __repr__(self):
        return "<User('%s', '%s', '%s')>" % \
                (self.id, self.name, self.email)

    def authenticate(self, password):
        secret = password+self.salt
        return self.hash == hashlib.sha512(secret).hexdigest()


class UserRelation(Base):
    __tablename__ = 'user_relations'

    id = Column(BigInteger, Sequence(
        'seq_user_relation_id', start=1, increment=1), primary_key=True)
    user_id = Column(Integer, nullable=False)
    chap_id = Column(Integer, nullable=False)
    is_banned = Column(Boolean, default=False)

    def __repr__(self):
        return "<UserRelation('%s user:%s, chap:%s)" % \
               (self.id, self.user_id, self.chap_id)
