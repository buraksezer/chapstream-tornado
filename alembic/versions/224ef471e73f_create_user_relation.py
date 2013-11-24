"""Create user_relations table

Revision ID: 224ef471e73f
Revises: None
Create Date: 2013-11-25 01:34:43.505916

"""

# revision identifiers, used by Alembic.
revision = '224ef471e73f'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'user_relations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('chap_id', sa.Integer, nullable=False),
        sa.Column('is_banned', sa.Boolean, default=False)
    )

def downgrade():
    op.drop_table('user_relations')
