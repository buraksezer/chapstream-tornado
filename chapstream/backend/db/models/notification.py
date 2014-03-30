from sqlalchemy import func
from sqlalchemy import Column, DateTime, Integer, \
    ForeignKey, Boolean, Sequence, \
    BigInteger

from chapstream.backend.db.models.user import User
from chapstream.backend.db.orm import Base
from chapstream.backend.db.orm import UnicodeJSONType


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(BigInteger, Sequence(
        'seq_notification_id', start=1, increment=1), primary_key=True)
    message = Column(UnicodeJSONType)
    is_read = Column(Boolean, default=False)
    user_id = Column(BigInteger, ForeignKey(User.id, ondelete='CASCADE'))
    created_at = Column(DateTime, default=func.current_timestamp())

    def __repr__(self):
        return "<Notification(id:'%s', user_id:'%s')>" \
               % (self.id, self.user_id)