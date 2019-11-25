"""added boolean

Revision ID: 11529d7ff6ac
Revises: c4a1774be008
Create Date: 2019-09-17 10:35:25.203043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11529d7ff6ac'
down_revision = 'c4a1774be008'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('excel_files', sa.Column('valid', sa.Boolean(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('excel_files', 'valid')
    # ### end Alembic commands ###