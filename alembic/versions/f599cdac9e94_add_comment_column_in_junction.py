"""add comment column in junction

Revision ID: f599cdac9e94
Revises: d131d7d393a4
Create Date: 2018-01-22 14:49:34.110007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f599cdac9e94'
down_revision = 'd131d7d393a4'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("alter table JUNCTION add column COMMENT varchar(500) default NULL;")


def downgrade():
    conn = op.get_bind()
    conn.execute("alter table JUNCTION drop column COMMENT;")
