from sqlalchemy import func
from sqlalchemy import Column, DateTime, UnicodeText, \
    Sequence, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from chapstream.backend.db.orm import Base
from chapstream.backend.db.models.user import User


class DirectMessageThread(Base):
    __tablename__ = "direct_message_threads"
    id = Column(BigInteger, Sequence(
        'seq_direct_message_thread_id', start=1, increment=1),
                primary_key=True)
    subject = Column(UnicodeText, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    user_id = Column(BigInteger, ForeignKey(User.id))
    user = relationship(User, primaryjoin=(User.id == user_id))
    chap_id = Column(BigInteger, ForeignKey(User.id))
    chap = relationship(User, primaryjoin=(User.id == chap_id))
    messages = relationship('DirectMessage',
                            backref='thread',
                            cascade="all, delete",
                            lazy='dynamic',
                            passive_deletes=True)

    def __repr__(self):
        return "<DirectMessageThread('id:%s user:%s, chap:%s subject:%s )" \
               % (self.id, self.user_id, self.chap_id, self.subject)


class DirectMessage(Base):
    __tablename__ = "direct_messages"
    id = Column(BigInteger, Sequence(
        'seq_direct_message_id', start=1, increment=1), primary_key=True)
    body = Column(UnicodeText, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    thread_id = Column(BigInteger, ForeignKey(DirectMessageThread.id,
                                              ondelete='CASCADE'))

    def __repr__(self):
        return "<DirectMessage('id:%s, thread:%s)" \
               % (self.id, self.thread.subject)



