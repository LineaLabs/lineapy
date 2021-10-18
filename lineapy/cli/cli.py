import logging
import os
import pathlib

import click
import rich
import rich.syntax
import rich.tree

from lineapy.constants import ExecutionMode
from lineapy.data.types import SessionType
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.instrumentation.tracer import Tracer
from lineapy.logging import configure_logging
from lineapy.transformer.node_transformer import transform
from lineapy.utils import prettify

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
    "--export-slice",
    default=None,
    help="Requires --slice. Export the sliced code that {slice} depends on to {export_slice}.py",
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
@click.option(
    "--visualize",
    help="Visualize the resulting graph with Graphviz",
    is_flag=True,
)
@click.argument(
    "file_name",
    type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
)
def linea_cli(
    file_name: pathlib.Path,
    mode,
    slice,
    export_slice,
    print_source,
    print_graph,
    verbose,
    visualize,
):
    configure_logging("INFO" if verbose else "WARNING")
    tree = rich.tree.Tree(f"📄 {file_name}")

    execution_mode = ExecutionMode.__getitem__(str.upper(mode))
    db = RelationalLineaDB.from_environment(execution_mode)
    code = file_name.read_text()

    if print_source:
        tree.add(
            rich.console.Group(
                "Source code", rich.syntax.Syntax(code, "python")
            )
        )

    # Change the working directory to that of the script,
    # To pick up relative data paths
    os.chdir(file_name.parent)

    tracer = Tracer(db, SessionType.SCRIPT)
    transform(code, file_name, tracer)

    if visualize:
        tracer.visualize()
    if slice and not export_slice:
        tree.add(
            rich.console.Group(
                f"Slice of {repr(slice)}",
                rich.syntax.Syntax(tracer.slice(slice), "python"),
            )
        )

    if export_slice:
        if not slice:
            print("Please specify --slice. It is required for --export-slice")
            exit(1)
        full_code = tracer.sliced_func(slice, export_slice)
        pathlib.Path(f"{export_slice}.py").write_text(full_code)

    tracer.db.close()
    if print_graph:
        graph_code = prettify(
            tracer.graph.print(
                include_source_location=False,
                include_id_field=False,
                include_session=False,
                include_imports=False,
            )
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
