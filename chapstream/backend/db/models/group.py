from sqlalchemy import func
from sqlalchemy import Table, Column, DateTime, Boolean, \
    UnicodeText, Sequence, BigInteger, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from chapstream.backend.db.orm import Base


group_posts = Table(
    "group_posts",
    Base.metadata,
    Column("gp_group", Integer, ForeignKey("groups.id")),
    Column("gp_post", Integer, ForeignKey("posts.id")),
)


class Group(Base):
    __tablename__ = 'groups'

    id = Column(BigInteger, Sequence(
        'seq_group_id', start=1, increment=1), primary_key=True)
    name = Column(String, nullable=False)
    summary = Column(UnicodeText)
    is_private = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    posts = relationship('Post', backref='group',
                         secondary=group_posts, lazy='dynamic')
    created_at = Column(DateTime, default=func.current_timestamp())

    def __repr__(self):
        return "<Group(id:'%s', name:'%s')>" \
               % (self.id, self.name)