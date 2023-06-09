"""Refactor user

Revision ID: e9c13e6c3ecd
Revises: dea2700aee29
Create Date: 2023-04-28 01:22:41.921938

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "e9c13e6c3ecd"
down_revision = "dea2700aee29"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user", sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False)
    )
    op.add_column(
        "user",
        sa.Column("last_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column("user", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("user", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.alter_column("user", "disabled", existing_type=sa.BOOLEAN(), nullable=True)
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=False)
    op.drop_column("user", "full_name")
    op.drop_column("user", "username")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user", sa.Column("username", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "user",
        sa.Column("full_name", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.alter_column("user", "disabled", existing_type=sa.BOOLEAN(), nullable=False)
    op.drop_column("user", "updated_at")
    op.drop_column("user", "created_at")
    op.drop_column("user", "last_name")
    op.drop_column("user", "name")
    # ### end Alembic commands ###
