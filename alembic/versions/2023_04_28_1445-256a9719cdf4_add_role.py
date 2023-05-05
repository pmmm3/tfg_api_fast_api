"""Add Role

Revision ID: 256a9719cdf4
Revises: e9c13e6c3ecd
Create Date: 2023-04-28 14:45:06.877166

"""
import sqlalchemy
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "256a9719cdf4"
down_revision = "e9c13e6c3ecd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("role", sqlalchemy.String(), nullable=False))
    op.create_index(op.f("ix_user_role"), "user", ["role"], unique=False)
    op.alter_column("user", "disabled", existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column(
        "user", "created_at", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        "user", "updated_at", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_user_role"), table_name="user")
    op.drop_column("user", "role")
    op.alter_column(
        "user", "updated_at", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        "user", "created_at", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column("user", "disabled", existing_type=sa.BOOLEAN(), nullable=True)
    # ### end Alembic commands ###