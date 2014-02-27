from sqlalchemy import func
from sqlalchemy import Column, Integer, \
    DateTime, Boolean, UnicodeText, ForeignKey, \
    Sequence, BigInteger

from chapstream.backend.db.models.user import User
from chapstream.backend.db.orm import Base


class Post(Base):
    __tablename__ = 'posts'

    id = Column(BigInteger, Sequence(
        'seq_post_id', start=1, increment=1), primary_key=True)
    body = Column(UnicodeText, nullable=True)
    is_draft = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'))

    def __repr__(self):
        return "<Post(id: '%s', user_id: '%s')>" % \
                (self.id, self.user_id)
