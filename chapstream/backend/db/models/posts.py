from sqlalchemy import Column, Integer, \
                DateTime, Boolean, UnicodeText, ForeignKey
from sqlalchemy import func

from chapstream.backend.db import Base


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    body = Column(UnicodeText, nullable=True)
    is_draft = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return "<Post('%s')>" % self.id
