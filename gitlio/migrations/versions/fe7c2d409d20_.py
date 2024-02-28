"""empty message

Revision ID: fe7c2d409d20
Revises: 
Create Date: 2024-02-22 20:56:33.814862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe7c2d409d20'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), unique=True, index=True),
        sa.Column('is_active', sa.Boolean(), default=True)
    )


def downgrade() -> None:
    op.drop_table('users')
