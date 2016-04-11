"""add avatar_hash

Revision ID: 04c3294886d9
Revises: None
Create Date: 2016-04-11 14:24:48.646862

"""

# revision identifiers, used by Alembic.
revision = '04c3294886d9'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar_hash', sa.String(length=32), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_hash')
    ### end Alembic commands ###