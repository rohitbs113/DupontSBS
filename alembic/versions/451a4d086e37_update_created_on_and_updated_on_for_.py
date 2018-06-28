"""update created_on and updated_on for system

Revision ID: 451a4d086e37
Revises: 64ec7fb1760d
Create Date: 2018-02-12 18:40:02.376592

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '451a4d086e37'
down_revision = '64ec7fb1760d'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("update USER_ROLE set CREATED_ON=now(),UPDATED_ON=now() where USERNAME='system';")


def downgrade():
    pass
