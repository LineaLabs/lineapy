# Code based on https://improveandrepeat.com/2021/09/python-friday-87-handling-pre-existing-tables-with-alembic-and-sqlalchemy/
# Code based on https://github.com/talkpython/data-driven-web-apps-with-flask

from alembic import op
from sqlalchemy import engine_from_config, inspect


def table_exists(table, schema=None):
    config = op.get_context().config
    engine = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy."
    )
    insp = inspect(engine)
    return insp.has_table(table, schema)


def maybe_create_table(name, *args, **kwargs):
    if not table_exists(name):
        op.create_table(name, *args, **kwargs)


def table_has_column(table, column):
    config = op.get_context().config
    engine = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy."
    )
    insp = inspect(engine)
    return any([column.name == col["name"] for col in insp.get_columns(table)])


def maybe_add_column(table_name, column, *args, **kwargs):
    if not table_has_column(table_name, column):
        op.add_column(table_name, column, *args, **kwargs)
