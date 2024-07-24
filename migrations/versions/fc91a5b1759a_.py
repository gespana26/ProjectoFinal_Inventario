"""empty message

Revision ID: fc91a5b1759a
Revises: 63bb8e9542f9
Create Date: 2024-07-24 01:00:11.461611

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc91a5b1759a'
down_revision = '63bb8e9542f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('address',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=60), nullable=False),
    sa.Column('city', sa.String(length=60), nullable=False),
    sa.Column('country', sa.String(length=60), nullable=False),
    sa.Column('nit', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['nit'], ['customer.nit'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('categoryproduct',
    sa.Column('idCatProd', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('idCatProd')
    )
    op.create_table('customer',
    sa.Column('nit', sa.Integer(), nullable=False),
    sa.Column('phone', sa.String(length=60), nullable=False),
    sa.Column('date', sa.String(length=15), nullable=False),
    sa.Column('id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['address.id'], ),
    sa.PrimaryKeyConstraint('nit')
    )
    op.create_table('products',
    sa.Column('id_prod', sa.Integer(), nullable=False),
    sa.Column('prodname', sa.String(length=60), nullable=False),
    sa.Column('salesPrice', sa.Integer(), nullable=False),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.Column('idCatProd', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['idCatProd'], ['categoryproduct.idCatProd'], ),
    sa.PrimaryKeyConstraint('id_prod')
    )
    op.create_table('provider',
    sa.Column('nit', sa.Integer(), nullable=False),
    sa.Column('phone', sa.String(length=60), nullable=False),
    sa.Column('id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['address.id'], ),
    sa.PrimaryKeyConstraint('nit')
    )
    op.create_table('sales',
    sa.Column('idSales', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=15), nullable=False),
    sa.Column('totalPrice', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=True),
    sa.Column('nit', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['nit'], ['customer.nit'], ),
    sa.PrimaryKeyConstraint('idSales')
    )
    op.create_table('detailsales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('unitPrice', sa.Integer(), nullable=False),
    sa.Column('idSales', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['idSales'], ['sales.idSales'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('profile')

    op.drop_table('detailsales')
    op.drop_table('sales')
    op.drop_table('provider')
    op.drop_table('products')
    op.drop_table('customer')
    op.drop_table('categoryproduct')
    op.drop_table('address')
    # ### end Alembic commands ###
