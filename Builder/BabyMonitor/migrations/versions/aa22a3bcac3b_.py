import geoalchemy2
"""empty message

Revision ID: aa22a3bcac3b
Revises: 2d4e0870ade3
Create Date: 2020-01-23 13:45:13.543502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa22a3bcac3b'
down_revision = '2d4e0870ade3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('smart_tv_command_sensor_data', sa.Column('status', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('smart_tv_command_sensor_data', 'status')
    # ### end Alembic commands ###
