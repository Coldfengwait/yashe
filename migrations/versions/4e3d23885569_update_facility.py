"""update_facility

Revision ID: 4e3d23885569
Revises: 500155d9dbb8
Create Date: 2019-03-07 09:53:58.209066

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4e3d23885569'
down_revision = '500155d9dbb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ys_facility_info', sa.Column('name', sa.String(length=32), nullable=False))
    op.drop_constraint(u'ys_facility_info_ibfk_1', 'ys_facility_info', type_='foreignkey')
    op.drop_column('ys_facility_info', 'url')
    op.drop_column('ys_facility_info', 'house_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ys_facility_info', sa.Column('house_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.add_column('ys_facility_info', sa.Column('url', mysql.VARCHAR(length=256), nullable=False))
    op.create_foreign_key(u'ys_facility_info_ibfk_1', 'ys_facility_info', 'ys_hosue_info', ['house_id'], ['id'])
    op.drop_column('ys_facility_info', 'name')
    # ### end Alembic commands ###
