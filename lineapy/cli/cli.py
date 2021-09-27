import os
from tempfile import NamedTemporaryFile
import click

from lineapy.data.types import SessionType
from lineapy.transformer.transformer import ExecutionMode, Transformer
from lineapy.utils import info_log, report_error_to_user, set_debug
from lineapy.cli.utils import run_transformed

"""
We are using click because our package will likely already have a dependency on
  flask and it's fairly well-starred.
"""


@click.command()
@click.option(
    "--mode",
    default="dev",
    help="Either `dev`, `test`, or `prod` mode",
)
@click.option(
    "--session",
    default=SessionType.SCRIPT.name,
    help=(
        f"Either `f{SessionType.STATIC.name}`,"
        f"or `f{SessionType.SCRIPT.name}` mode"
    ),
)
@click.argument("file_name")
def linea_cli(mode, session, file_name):
    execution_mode = ExecutionMode.__getitem__(str.upper(mode))
    if execution_mode == ExecutionMode.PROD:
        set_debug(False)
    session_type = SessionType.__getitem__(str.upper(session))
    try:
        run_transformed(file_name, session_type, execution_mode)

    except IOError:
        report_error_to_user("Error: File does not appear to exist.")
        return


if __name__ == "__main__":
    linea_cli()
