"""Initial migration

Revision ID: 0cd437e0ee7d
Revises: cf9ee25e5909
Create Date: 2020-03-16 18:19:11.896508

"""

# revision identifiers, used by Alembic.
revision = '0cd437e0ee7d'
down_revision = 'cf9ee25e5909'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sticker', sa.Column('fileSize', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sticker', 'fileSize')
    # ### end Alembic commands ###
