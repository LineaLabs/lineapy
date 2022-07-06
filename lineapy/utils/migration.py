# Code based on https://improveandrepeat.com/2021/09/python-friday-87-handling-pre-existing-tables-with-alembic-and-sqlalchemy/
# Code based on https://github.com/talkpython/data-driven-web-apps-with-flask

from alembic import op
from sqlalchemy import engine_from_config, inspect

from lineapy.utils.config import options


def table_exists(table, schema=None):
    engine = engine_from_config(
        {"sqlalchemy.url": options.database_url}, prefix="sqlalchemy."
    )
    insp = inspect(engine)
    return insp.has_table(table, schema)


def ensure_table(name, *args, **kwargs):
    if not table_exists(name):
        op.create_table(name, *args, **kwargs)


def table_has_column(table, column):
    engine = engine_from_config(
        {"sqlalchemy.url": options.database_url}, prefix="sqlalchemy."
    )
    insp = inspect(engine)
    return any([column == col["name"] for col in insp.get_columns(table)])


def ensure_column(table_name, column, *args, **kwargs):
    if not table_has_column(table_name, column.name):
        op.add_column(table_name, column, *args, **kwargs)
