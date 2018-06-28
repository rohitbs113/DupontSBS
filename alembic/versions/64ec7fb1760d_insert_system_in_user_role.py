"""insert system in user_role

Revision ID: 64ec7fb1760d
Revises: d4c019702668
Create Date: 2018-02-06 15:41:11.005529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64ec7fb1760d'
down_revision = 'd4c019702668'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("INSERT IGNORE into USER_ROLE(CREATED_ON,UPDATED_ON,USERNAME,ROLE,ACTIVE,CREATED_BY,UPDATED_BY) values('2017-07-10 00:00:00','2017-07-10 00:00:00','system','lab',1,'system','system');")


def downgrade():
    pass
