"""add column commented_by junction table

Revision ID: 852d0134f0ad
Revises: f599cdac9e94
Create Date: 2018-01-24 18:04:21.141006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '852d0134f0ad'
down_revision = 'f599cdac9e94'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("alter table JUNCTION add column COMMENTED_BY varchar(50);")
    conn.execute("ALTER TABLE JUNCTION ADD CONSTRAINT fk_commented_by FOREIGN KEY (COMMENTED_BY) REFERENCES USER_ROLE(USERNAME);")


def downgrade():
    conn = op.get_bind()
    conn.execute("alter table JUNCTION drop FOREIGN KEY fk_commented_by;")
    conn.execute("alter table JUNCTION drop column COMMENTED_BY;")
