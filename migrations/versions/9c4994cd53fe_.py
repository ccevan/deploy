"""empty message

Revision ID: 9c4994cd53fe
Revises: 
Create Date: 2019-02-27 17:55:19.514587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c4994cd53fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tbserverversionrel',
    sa.Column('server_id', sa.String(length=32), nullable=False),
    sa.Column('version_id', sa.String(length=32), nullable=False),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['tbserver.id'], ),
    sa.ForeignKeyConstraint(['version_id'], ['tbversion.id'], ),
    sa.PrimaryKeyConstraint('server_id', 'version_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tbserverversionrel')
    # ### end Alembic commands ###
