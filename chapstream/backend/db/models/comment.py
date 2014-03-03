from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Integer, String, \
    DateTime, UnicodeText, ForeignKey, \
    Sequence, BigInteger

from chapstream.backend.db.models.user import User
from chapstream.backend.db.models.post import Post
from chapstream.backend.db.orm import Base


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(BigInteger, Sequence(
        'seq_comment_id', start=1, increment=1), primary_key=True)
    body = Column(UnicodeText, nullable=True)
    likes = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'))
    post_id = Column(Integer, ForeignKey(Post.id, ondelete='CASCADE'))

    def __repr__(self):
        return "<Comment(id: '%s', user_id: '%s', post_id: '%s')>" % \
               (self.id, self.user_id, self.post_id)
