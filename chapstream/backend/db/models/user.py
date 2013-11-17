import hashlib
from datetime import datetime

from sqlalchemy import Column, Integer, \
                String, DateTime, Boolean, UnicodeText
from sqlalchemy.orm import relationship

from chapstream.backend.db import Base
from chapstream.backend.db.models.posts import Post

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    fullname = Column(String)
    email = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    bio = Column(UnicodeText, nullable=True)
    sign_up_date = Column(DateTime, default=datetime.utcnow())
    last_seen = Column(DateTime, default=datetime.utcnow())
    posts = relationship("Post", backref='user')

    def __repr__(self):
        return "<User('%s', '%s', '%s')>" % \
                (self.id, self.name, self.email)

    def authenticate(self, password):
        secret = password+self.salt
        return self.hash == hashlib.sha512(secret).hexdigest()