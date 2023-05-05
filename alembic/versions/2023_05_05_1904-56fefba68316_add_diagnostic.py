"""Add diagnostic

Revision ID: 56fefba68316
Revises: b640034a0c51
Create Date: 2023-05-05 19:04:10.253654

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "56fefba68316"
down_revision = "b640034a0c51"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "diagnostic",
        sa.Column("id", sa.Integer(), nullable=True),
        sa.Column("questions_ids", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("value_question", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "diagnostic_result", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["module_id"],
            ["module.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("diagnostic")
    # ### end Alembic commands ###
