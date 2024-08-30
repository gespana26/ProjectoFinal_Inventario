"""empty message

Revision ID: 296a1eb81ebb
Revises: 8664e34e682d
Create Date: 2024-08-29 20:04:01.205843

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '296a1eb81ebb'
down_revision = '8664e34e682d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('states',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('state_name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('state_name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('states')
    # ### end Alembic commands ###
