import logging
import pathlib
from typing import cast

import click
import rich
import rich.syntax
import rich.tree

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID, SessionType
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.logging import configure_logging
from lineapy.transformer.transformer import ExecutionMode, Transformer

"""
We are using click because our package will likely already have a dependency on
  flask and it's fairly well-starred.
"""

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--mode",
    default="memory",
    help="Either `memory`, `dev`, `test`, or `prod` mode",
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
@click.option(
    "--verbose",
    help="Print out logging for graph creation and execution",
    is_flag=True,
)
@click.argument("file_name")
def linea_cli(mode, file_name, slice, print_source, print_graph, verbose):
    configure_logging("INFO" if verbose else "WARNING")
    tree = rich.tree.Tree(f"📄 {file_name}")

    execution_mode = ExecutionMode.__getitem__(str.upper(mode))

    transformer = Transformer()

    try:
        code = pathlib.Path(file_name).read_text()
    except IOError:
        logger.exception("Error: File does not appear to exist.")
        return

    if print_source:
        tree.add(
            rich.console.Group(
                "Source code", rich.syntax.Syntax(code, "python")
            )
        )

    tracer = transformer.transform(
        code,
        session_type=SessionType.SCRIPT,
        path=file_name,
        execution_mode=ExecutionMode.MEMORY,
    )

    db = tracer.records_manager.db
    nodes = db.get_all_nodes()
    context = tracer.session_context
    graph = Graph(nodes, context)

    if slice:
        artifact = db.get_artifact_by_name(slice)
        sliced_code = get_program_slice(graph, [cast(LineaID, artifact.id)])
        tree.add(
            rich.console.Group(
                f"Slice of {repr(slice)}",
                rich.syntax.Syntax(sliced_code, "python"),
            )
        )

    if print_graph:
        graph_code = graph.print(
            include_source_location=False,
            include_id_field=False,
            include_session=False,
            include_imports=False,
        )
        tree.add(
            rich.console.Group(
                "፨ Graph", rich.syntax.Syntax(graph_code, "python")
            )
        )

    console = rich.console.Console()
    console.print(tree)


if __name__ == "__main__":
    linea_cli()
