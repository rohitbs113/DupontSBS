"""modify unique reads and supporting reads columns of junction table

Revision ID: b749d119f5da
Revises: 451a4d086e37
Create Date: 2018-03-07 13:59:04.646538

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b749d119f5da'
down_revision = '451a4d086e37'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("ALTER TABLE JUNCTION MODIFY UNIQUE_READS BIGINT(20) UNSIGNED;")
    conn.execute("ALTER TABLE JUNCTION MODIFY SUPPORTING_READS BIGINT(20) UNSIGNED;")


def downgrade():
    pass
