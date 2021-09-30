import click
from lineapy.data.graph import Graph

from lineapy.data.types import SessionType
from lineapy.transformer.transformer import ExecutionMode
from lineapy.utils import report_error_to_user, set_debug
from lineapy.cli.utils import run_transformed
from lineapy.graph_reader.program_slice import get_program_slice

"""
We are using click because our package will likely already have a dependency on
  flask and it's fairly well-starred.
"""


@click.command()
@click.option(
    "--mode",
    default="memory",
    help="Either `memory`, `dev`, `test`, or `prod` mode",
)
@click.option(
    "--session",
    default=SessionType.STATIC.name,
    help=(
        f"Either `{SessionType.STATIC.name}`,"
        f"or `{SessionType.SCRIPT.name}` mode"
    ),
)
@click.option(
    "--slice",
    default=None,
    help="Print the sliced code that this artifact depends on",
)
@click.option(
    "--print-source",
    default=False,
    help="Whether to print the source code",
)
@click.option(
    "--print-graph",
    default=False,
    help="Whether to print the generated graph code",
)
@click.argument("file_name")
def linea_cli(mode, session, file_name, slice, print_source, print_graph):
    execution_mode = ExecutionMode.__getitem__(str.upper(mode))
    if execution_mode == ExecutionMode.PROD:
        set_debug(False)
    session_type = SessionType.__getitem__(str.upper(session))
    try:
        tracer = run_transformed(
            file_name, session_type, execution_mode, print_source
        )

    except IOError:
        report_error_to_user("Error: File does not appear to exist.")
        return
    db = tracer.records_manager.db
    nodes = db.get_all_nodes()
    context = db.get_context_by_file_name(file_name)
    graph = Graph(nodes, context)

    if print_graph:
        print("Generated Graph:\n")
        print(graph)
    if slice:
        print("Sliced Code\n")
        artifact = db.get_artifact_by_name(slice)
        sliced_code = get_program_slice(graph, [artifact.id])
        print(sliced_code)


if __name__ == "__main__":
    linea_cli()
