"""empty message

Revision ID: 95f843d0d528
Revises: 
Create Date: 2024-09-11 14:56:09.327141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '95f843d0d528'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('hotels',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('hotels')
