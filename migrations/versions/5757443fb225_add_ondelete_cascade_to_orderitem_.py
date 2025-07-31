"""Add ondelete cascade to OrderItem.animal_id

Revision ID: 5757443fb225
Revises: c10948cae788
Create Date: 2025-07-31 23:34:04.335460
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '5757443fb225'
down_revision = 'c10948cae788'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('order_items') as batch_op:
        batch_op.drop_constraint('order_items_animal_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key('order_items_animal_id_fkey', 'animals', ['animal_id'], ['id'], ondelete='CASCADE')

    # Optional: if you're altering more things, restore/recreate dropped FKs if required
    # NOTE: The other drop_constraints in your original script (like on animal_images) are not redone
    # here, so they’ll be missing from the upgraded DB unless recreated explicitly.


def downgrade():
    with op.batch_alter_table('order_items') as batch_op:
        batch_op.drop_constraint('order_items_animal_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key('order_items_animal_id_fkey', 'animals', ['animal_id'], ['id'])
