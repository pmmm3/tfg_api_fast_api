"""Add questions

Revision ID: b640034a0c51
Revises: 8a4c13155a0d
Create Date: 2023-05-05 18:54:12.213620

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "b640034a0c51"
down_revision = "8a4c13155a0d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "module",
        sa.Column("id", sa.Integer(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "question",
        sa.Column("id", sa.Integer(), nullable=True),
        sa.Column("question_text", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.Column("dependent_question_id", sa.Integer(), nullable=True),
        sa.Column(
            "dependent_response", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["module_id"],
            ["module.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "questiondependency",
        sa.Column("parent_question_id", sa.Integer(), nullable=False),
        sa.Column("child_question_id", sa.Integer(), nullable=False),
        sa.Column("answer_required", sa.Boolean(), nullable=False),
        sa.Column("answer_value", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["child_question_id"],
            ["question.id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_question_id"],
            ["question.id"],
        ),
        sa.PrimaryKeyConstraint("parent_question_id", "child_question_id"),
    )
    op.create_table(
        "questionnairemodulelink",
        sa.Column("questionnaire_id", sa.Integer(), nullable=True),
        sa.Column("module_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["module_id"],
            ["module.id"],
        ),
        sa.ForeignKeyConstraint(
            ["questionnaire_id"],
            ["questionnaire.id"],
        ),
        sa.PrimaryKeyConstraint("questionnaire_id", "module_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("questionnairemodulelink")
    op.drop_table("questiondependency")
    op.drop_table("question")
    op.drop_table("module")
    # ### end Alembic commands ###
