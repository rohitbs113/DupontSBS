"""add index in table

Revision ID: 19e686975320
Revises: 
Create Date: 2017-10-10 10:40:03.594454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19e686975320'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("CREATE INDEX REQUEST_REQUEST_ID_INDEX ON REQUEST (REQUEST_ID);")
    conn.execute("CREATE INDEX SAMPLE_EVENT_ID_INDEX ON SAMPLE (EVENT_ID);")


def downgrade():
    conn = op.get_bind()
    conn.execute("DROP INDEX REQUEST_REQUEST_ID_INDEX ON REQUEST (REQUEST_ID);")
    conn.execute("DROP INDEX SAMPLE_EVENT_ID_INDEX ON SAMPLE (EVENT_ID);")
