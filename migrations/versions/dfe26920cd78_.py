"""empty message

Revision ID: dfe26920cd78
Revises: 66aaa7cce8a5
Create Date: 2018-05-23 11:22:17.179395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfe26920cd78'
down_revision = '66aaa7cce8a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('access', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'access')
    # ### end Alembic commands ###
