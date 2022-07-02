"""orig

Revision ID: 38d5f834d3b7
Revises: 
Create Date: 2022-06-27 18:10:07.339148

"""
import sqlalchemy as sa
from alembic import op

from lineapy.utils.migration import ensure_table, table_has_column

# revision identifiers, used by Alembic.
revision = "38d5f834d3b7"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    ensure_table(
        "execution",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    ensure_table(
        "source_code",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("jupyter_execution_count", sa.Integer(), nullable=True),
        sa.Column("jupyter_session_id", sa.String(), nullable=True),
        sa.CheckConstraint(
            "(jupyter_execution_count IS NULL) = (jupyter_session_id is NULL)"
        ),
        sa.CheckConstraint(
            "(path IS NOT NULL) != ((jupyter_execution_count IS NOT NULL) AND (jupyter_execution_count IS NOT NULL))"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    ensure_table(
        "node",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=True),
        sa.Column(
            "node_type",
            sa.Enum(
                "Node",
                "CallNode",
                "LiteralNode",
                "ImportNode",
                "LookupNode",
                "MutateNode",
                "GlobalNode",
                name="nodetype",
            ),
            nullable=True,
        ),
        sa.Column("lineno", sa.Integer(), nullable=True),
        sa.Column("col_offset", sa.Integer(), nullable=True),
        sa.Column("end_lineno", sa.Integer(), nullable=True),
        sa.Column("end_col_offset", sa.Integer(), nullable=True),
        sa.Column("source_code_id", sa.String(), nullable=True),
        sa.CheckConstraint(
            "(lineno IS NULL) = (col_offset is NULL) and (col_offset is NULL) = (end_lineno is NULL) and (end_lineno is NULL) = (end_col_offset is NULL) and (end_col_offset is NULL) = (source_code_id is NULL)"
        ),
        sa.ForeignKeyConstraint(
            ["source_code_id"],
            ["source_code.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    ensure_table(
        "session_context",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "environment_type",
            sa.Enum("JUPYTER", "SCRIPT", name="sessiontype"),
            nullable=True,
        ),
        sa.Column("creation_time", sa.DateTime(), nullable=True),
        sa.Column("working_directory", sa.String(), nullable=True),
        sa.Column("session_name", sa.String(), nullable=True),
        sa.Column("user_name", sa.String(), nullable=True),
        sa.Column("hardware_spec", sa.String(), nullable=True),
        sa.Column("execution_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["execution_id"],
            ["execution.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    if not table_has_column("session_context", "python_version"):
        op.add_column(
            "session_context", sa.Column("python_version", sa.String)
        )
        op.execute('UPDATE session_context SET python_version = ""')

    ensure_table(
        "artifact",
        sa.Column("node_id", sa.String(), nullable=False),
        sa.Column("execution_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["execution_id"],
            ["execution.id"],
        ),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["node.id"],
        ),
        sa.PrimaryKeyConstraint("node_id", "execution_id", "name", "version"),
    )
    ensure_table(
        "call_node",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("function_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["function_id"],
            ["node.id"],
        ),
        sa.ForeignKeyConstraint(
            ["id"],
            ["node.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    ensure_table(
        "global_node",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("call_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["call_id"],
            ["node.id"],
        ),
        sa.ForeignKeyConstraint(
            ["id"],
            ["node.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    ensure_table(
        "import_node",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("package_name", sa.String(), nullable=True),
        sa.Column("version", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["node.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    ensure_table(
        "literal_assign_node",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "value_type",
            sa.Enum(
                "String",
                "Integer",
                "Float",
                "Boolean",
                "NoneType",
                "Ellipsis",
                name="literaltype",
            ),
            nullable=True,
        ),
        sa.Column("value", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["node.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    ensure_table(
        "lookup",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["node.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    ensure_table(
        "mutate_node",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("source_id", sa.String(), nullable=True),
        sa.Column("call_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["call_id"],
            ["node.id"],
        ),
        sa.ForeignKeyConstraint(
            ["id"],
            ["node.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["node.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    ensure_table(
        "node_value",
        sa.Column("node_id", sa.String(), nullable=False),
        sa.Column("execution_id", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=True),
        sa.Column(
            "value_type",
            sa.Enum(
                "chart", "array", "dataset", "code", "value", name="valuetype"
            ),
            nullable=True,
        ),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["execution_id"],
            ["execution.id"],
        ),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["node.id"],
        ),
        sa.PrimaryKeyConstraint("node_id", "execution_id"),
    )
    ensure_table(
        "global_reference",
        sa.Column("call_node_id", sa.String(), nullable=False),
        sa.Column("variable_node_id", sa.String(), nullable=False),
        sa.Column("variable_name", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["call_node_id"],
            ["call_node.id"],
        ),
        sa.ForeignKeyConstraint(
            ["variable_node_id"],
            ["node.id"],
        ),
        sa.PrimaryKeyConstraint(
            "call_node_id", "variable_node_id", "variable_name"
        ),
    )
    ensure_table(
        "implicit_dependency",
        sa.Column("call_node_id", sa.String(), nullable=False),
        sa.Column("arg_node_id", sa.String(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["arg_node_id"],
            ["node.id"],
        ),
        sa.ForeignKeyConstraint(
            ["call_node_id"],
            ["call_node.id"],
        ),
        sa.PrimaryKeyConstraint("call_node_id", "arg_node_id", "index"),
    )
    ensure_table(
        "keyword_arg",
        sa.Column("call_node_id", sa.String(), nullable=False),
        sa.Column("arg_node_id", sa.String(), nullable=False),
        sa.Column("starred", sa.Boolean(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["arg_node_id"],
            ["node.id"],
        ),
        sa.ForeignKeyConstraint(
            ["call_node_id"],
            ["call_node.id"],
        ),
        sa.PrimaryKeyConstraint("call_node_id", "arg_node_id", "name"),
    )
    ensure_table(
        "positional_arg",
        sa.Column("call_node_id", sa.String(), nullable=False),
        sa.Column("arg_node_id", sa.String(), nullable=False),
        sa.Column("starred", sa.Boolean(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["arg_node_id"],
            ["node.id"],
        ),
        sa.ForeignKeyConstraint(
            ["call_node_id"],
            ["call_node.id"],
        ),
        sa.PrimaryKeyConstraint("call_node_id", "arg_node_id", "index"),
    )


def downgrade() -> None:
    op.drop_table("positional_arg")
    op.drop_table("keyword_arg")
    op.drop_table("implicit_dependency")
    op.drop_table("global_reference")
    op.drop_table("node_value")
    op.drop_table("mutate_node")
    op.drop_table("lookup")
    op.drop_table("literal_assign_node")
    op.drop_table("import_node")
    op.drop_table("global_node")
    op.drop_table("call_node")
    op.drop_table("artifact")
    op.drop_table("session_context")
    op.drop_table("node")
    op.drop_table("source_code")
    op.drop_table("execution")
