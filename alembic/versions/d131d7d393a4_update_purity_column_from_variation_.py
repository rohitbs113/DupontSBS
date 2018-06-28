"""update purity column from variation table

Revision ID: d131d7d393a4
Revises: 19e686975320
Create Date: 2018-01-17 16:55:50.660852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd131d7d393a4'
down_revision = '19e686975320'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("ALTER TABLE VARIATION MODIFY COLUMN PURITY DECIMAL(6,5) default NULL")


def downgrade():
    pass
