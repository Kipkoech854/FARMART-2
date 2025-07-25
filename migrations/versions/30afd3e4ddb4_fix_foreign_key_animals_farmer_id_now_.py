"""Fix foreign key: animals.farmer_id now references farmers.id

Revision ID: 30afd3e4ddb4
Revises: db4661359661
Create Date: 2025-07-26 00:30:51.150831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30afd3e4ddb4'
down_revision = 'db4661359661'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('animals', schema=None) as batch_op:
        batch_op.drop_constraint('fk_animals_farmer_id_users', type_='foreignkey')
        batch_op.create_foreign_key('fk_animals_farmer_id_users', 'farmers', ['farmer_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('animals', schema=None) as batch_op:
        batch_op.drop_constraint('fk_animals_farmer_id_users', type_='foreignkey')
        batch_op.create_foreign_key('fk_animals_farmer_id_users', 'users', ['farmer_id'], ['id'])

    # ### end Alembic commands ###
