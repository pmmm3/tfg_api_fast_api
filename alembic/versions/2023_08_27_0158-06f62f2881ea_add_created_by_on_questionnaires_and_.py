"""Add created_by on questionnaires, and move status to assignment

Revision ID: 06f62f2881ea
Revises: 3b756363268a
Create Date: 2023-08-27 01:58:01.799182

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "06f62f2881ea"
down_revision = "3b756363268a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "assignment",
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column(
        "questionnaire",
        sa.Column("created_by", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.create_foreign_key(None, "questionnaire", "user", ["created_by"], ["email"])
    op.drop_column("questionnaire", "status")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "questionnaire",
        sa.Column("status", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(None, "questionnaire", type_="foreignkey")
    op.drop_column("questionnaire", "created_by")
    op.drop_column("assignment", "status")
    # ### end Alembic commands ###
