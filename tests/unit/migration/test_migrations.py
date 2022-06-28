import pytest
from sqlalchemy import text


def test_38d5f834d3b7_orig(alembic_engine, alembic_runner):
    alembic_runner.migrate_up_to("38d5f834d3b7")

    with alembic_engine.connect() as conn:
        assert conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).fetchall() == [
            ("alembic_version",),
            ("execution",),
            ("source_code",),
            ("node",),
            ("session_context",),
            ("artifact",),
            ("call_node",),
            ("global_node",),
            ("import_node",),
            ("literal_assign_node",),
            ("lookup",),
            ("mutate_node",),
            ("node_value",),
            ("global_reference",),
            ("implicit_dependency",),
            ("keyword_arg",),
            ("positional_arg",),
        ]

        assert conn.execute(
            text(
                "SELECT 1 FROM PRAGMA_TABLE_INFO('session_context') WHERE name='python_version';"
            )
        ).fetchall() == [(1,)]
