import pathlib
import rich
import rich.tree
import rich.syntax
import click
from lineapy.data.graph import Graph

from lineapy.data.types import SessionType
from lineapy.transformer.transformer import ExecutionMode, Transformer
from lineapy.utils import report_error_to_user, set_debug
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
    "--print-source", help="Whether to print the source code", is_flag=True
)
@click.option(
    "--print-graph",
    help="Whether to print the generated graph code",
    is_flag=True,
)
@click.argument("file_name")
def linea_cli(mode, session, file_name, slice, print_source, print_graph):
    tree = rich.tree.Tree(f"📄 {file_name}")

    execution_mode = ExecutionMode.__getitem__(str.upper(mode))
    if execution_mode == ExecutionMode.PROD:
        set_debug(False)
    session_type = SessionType.__getitem__(str.upper(session))

    transformer = Transformer()

    try:
        code = pathlib.Path(file_name).read_text()
    except IOError:
        report_error_to_user("Error: File does not appear to exist.")
        return

    if print_source:
        tree.add(
            rich.console.Group(
                f"Source code", rich.syntax.Syntax(code, "python")
            )
        )

    transformer.transform(
        code,
        session_type=session_type,
        session_name=file_name,
        execution_mode=ExecutionMode.MEMORY,
    )

    db = transformer.tracer.records_manager.db
    nodes = db.get_all_nodes()
    context = db.get_context_by_file_name(file_name)
    graph = Graph(nodes, context)

    if slice:
        artifact = db.get_artifact_by_name(slice)
        sliced_code = get_program_slice(graph, [artifact.id])
        tree.add(
            rich.console.Group(
                f"Slice of {repr(slice)}",
                rich.syntax.Syntax(sliced_code, "python"),
            )
        )

    if print_graph:
        tree.add(
            rich.console.Group(
                "፨ Graph", rich.syntax.Syntax(str(graph), "python")
            )
        )

    console = rich.console.Console()
    console.print(tree)


if __name__ == "__main__":
    linea_cli()
