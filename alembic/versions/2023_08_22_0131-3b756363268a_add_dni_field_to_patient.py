"""Add dni field to patient

Revision ID: 3b756363268a
Revises: ff7027d66ab5
Create Date: 2023-08-22 01:31:36.980883

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "3b756363268a"
down_revision = "ff7027d66ab5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("admin_id_user_fkey", "admin", type_="foreignkey")
    op.create_foreign_key(None, "admin", "user", ["id_user"], ["email"])
    op.drop_constraint("doctor_id_user_fkey", "doctor", type_="foreignkey")
    op.create_foreign_key(None, "doctor", "user", ["id_user"], ["email"])
    op.add_column(
        "patient", sa.Column("dni", sqlmodel.sql.sqltypes.AutoString(), nullable=True)
    )
    op.drop_constraint("patient_id_user_fkey", "patient", type_="foreignkey")
    op.create_foreign_key(None, "patient", "user", ["id_user"], ["email"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "patient", type_="foreignkey")
    op.create_foreign_key(
        "patient_id_user_fkey",
        "patient",
        "user",
        ["id_user"],
        ["email"],
        ondelete="CASCADE",
    )
    op.drop_column("patient", "dni")
    op.drop_constraint(None, "doctor", type_="foreignkey")
    op.create_foreign_key(
        "doctor_id_user_fkey",
        "doctor",
        "user",
        ["id_user"],
        ["email"],
        ondelete="CASCADE",
    )
    op.drop_constraint(None, "admin", type_="foreignkey")
    op.create_foreign_key(
        "admin_id_user_fkey",
        "admin",
        "user",
        ["id_user"],
        ["email"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###
