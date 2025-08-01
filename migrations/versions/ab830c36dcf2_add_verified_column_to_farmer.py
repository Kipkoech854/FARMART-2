"""Add verified column to Farmer

Revision ID: ab830c36dcf2
Revises: 48e7ac0949ad
Create Date: 2025-07-19 14:49:45.747288

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab830c36dcf2'
down_revision = '48e7ac0949ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('farmers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('verified', sa.String(length=20), nullable=True))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('verified',
               existing_type=sa.BOOLEAN(),
               type_=sa.String(length=20),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('verified',
               existing_type=sa.String(length=20),
               type_=sa.BOOLEAN(),
               existing_nullable=True)

    with op.batch_alter_table('farmers', schema=None) as batch_op:
        batch_op.drop_column('verified')

    # ### end Alembic commands ###
