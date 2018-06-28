"""modify observed map and observed map comment table constraints

Revision ID: 1fda2a2e1f1a
Revises: 451a4d086e37
Create Date: 2018-03-07 16:53:03.501646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1fda2a2e1f1a'
down_revision = 'b749d119f5da'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("ALTER TABLE OBSERVED_MAP_COMMENT DROP FOREIGN KEY "
                 "OBSERVED_MAP_COMMENT_ibfk_1;")
    conn.execute("ALTER TABLE OBSERVED_MAP_COMMENT ADD CONSTRAINT "
                 "OBSERVED_MAP_COMMENT_ibfk_1 FOREIGN KEY (OBSERVED_MAP_ID) "
                 "REFERENCES OBSERVED_MAP(ID) ON DELETE CASCADE;")


def downgrade():
    pass
