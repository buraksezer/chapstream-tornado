import hashlib
from datetime import datetime

from sqlalchemy import Column, Integer,\
    String, DateTime, Boolean, UnicodeText, Sequence, \
    BigInteger, ForeignKey
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
    is_private = Column(Boolean, default=False)
    bio = Column(UnicodeText, nullable=True)
    sign_up_date = Column(DateTime, default=datetime.utcnow())
    last_seen = Column(DateTime, default=datetime.utcnow())
    posts = relationship('Post',
                         backref='user',
                         cascade="all, delete",
                         lazy='dynamic',
                         passive_deletes=True)
    notifications = relationship('Notification',
                                 cascade="all, delete",
                                 backref='user',
                                 lazy='dynamic',
                                 passive_deletes=True)
    comments = relationship('Comment',
                            backref='user',
                            cascade="all, delete",
                            lazy='dynamic',
                            passive_deletes=True)

    def __repr__(self):
        return "<User(id:'%s', name:'%s', email:'%s')>" % \
                (self.id, self.name, self.email)

    def authenticate(self, password):
        secret = password+self.salt
        return self.hash == hashlib.sha512(secret).hexdigest()


class UserRelation(Base):
    __tablename__ = "user_relations"
    id = Column(BigInteger, Sequence(
        'seq_user_relation_id', start=1, increment=1),
                primary_key=True)

    user_id = Column(BigInteger, ForeignKey(User.id))
    user = relationship(User, backref="chap_list",
                        primaryjoin=(User.id == user_id))
    chap_id = Column(BigInteger, ForeignKey(User.id))
    chap = relationship(User, backref="user_list",
                        primaryjoin=(User.id == chap_id))
    is_banned = Column(Boolean, default=False)

    def __repr__(self):
        return "<UserRelation('id:%s user:%s, chap:%s)" % \
               (self.id, self.user_id, self.chap_id)