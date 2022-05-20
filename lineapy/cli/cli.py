import ast
import glob
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import TextIOWrapper
from statistics import mean
from time import perf_counter
from typing import Iterable, List, Optional

import click
import nbformat
import rich
import rich.syntax
import rich.tree
import yaml
from nbconvert.preprocessors import ExecutePreprocessor
from rich.console import Console
from rich.progress import Progress

from lineapy.data.types import SessionType
from lineapy.db.db import RelationalLineaDB
from lineapy.db.utils import OVERRIDE_HELP_TEXT
from lineapy.exceptions.excepthook import set_custom_excepthook
from lineapy.graph_reader.apis import LineaArtifact
from lineapy.instrumentation.tracer import Tracer
from lineapy.plugins.airflow import AirflowPlugin
from lineapy.plugins.utils import slugify
from lineapy.transformer.node_transformer import transform
from lineapy.utils.analytics import send_lib_info_from_db
from lineapy.utils.benchmarks import distribution_change
from lineapy.utils.config import (
    CUSTOM_ANNOTATIONS_EXTENSION_NAME,
    custom_annotations_folder,
)
from lineapy.utils.logging_config import (
    LOGGING_ENV_VARIABLE,
    configure_logging,
)
from lineapy.utils.utils import prettify
from lineapy.utils.validate_annotation_spec import validate_spec

"""
We are using click because our package will likely already have a dependency on
  flask and it's fairly well-starred.
"""

logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "--verbose",
    help="Print out logging for graph creation and execution",
    is_flag=True,
)
def linea_cli(verbose: bool):
    # Set the logging env variable so its passed to subprocesses, like creating a jupyter kernel
    if verbose:
        os.environ[LOGGING_ENV_VARIABLE] = "DEBUG"
    configure_logging()


@linea_cli.command()
@click.argument("file", type=click.File())
@click.argument("artifact_name")
@click.argument("artifact_value", type=str)
@click.option(
    "--visualize-slice",
    type=click.Path(dir_okay=False, path_type=pathlib.Path),
    help="Create a visualization for the sliced code, save it to this path",
)
def notebook(
    file: TextIOWrapper,
    artifact_name: str,
    artifact_value: str,
    visualize_slice: Optional[pathlib.Path],
):
    """
    Executes the notebook FILE, saves the value ARTIFACT_VALUE with name ARTIFACT_NAME, and prints the sliced code.

    For example, if your notebooks as dataframe with value `df`, then this will print the slice for it:

        lineapy notebook my_notebook.ipynb my_df df

    You can also reference side effect values, like `file_system`

        lineapy notebook my_notebook.ipynb notebook_file_system lineapy.file_system
    """
    logger.info("Creating in memory notebook")
    # Create the notebook:
    notebook = nbformat.read(file, nbformat.NO_CONVERT)
    notebook["cells"].append(
        nbformat.v4.new_code_cell(
            generate_save_code(artifact_name, artifact_value, visualize_slice)
        )
    )

    # Run the notebook:
    setup_ipython_dir()
    exec_proc = ExecutePreprocessor(timeout=None)
    logger.info("Executing notebook")
    exec_proc.preprocess(notebook)

    # Print the slice:
    logger.info("Printing slice")
    # TODO: duplicated with `get` but no context set, should rewrite eventually
    # to not duplicate
    db = RelationalLineaDB.from_environment()
    artifact = db.get_artifact_by_name(artifact_name)
    # FIXME: mypy issue with SQLAlchemy, see https://github.com/python/typeshed/issues/974
    api_artifact = LineaArtifact(
        db=db,
        _execution_id=artifact.execution_id,
        _node_id=artifact.node_id,
        _session_id=artifact.node.session_id,
        _version=artifact.version,  # type: ignore
        name=artifact_name,
        date_created=artifact.date_created,  # type: ignore
    )
    # logger.info(api_artifact.get_code())
    print(api_artifact.get_code())


@linea_cli.command()
@click.argument(
    "path",
    type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
)
@click.argument("artifact_name")
@click.argument("artifact_value", type=str)
@click.option(
    "--visualize-slice",
    type=click.Path(dir_okay=False, path_type=pathlib.Path),
    help="Create a visualization for the sliced code, save it to this path",
)
def file(
    path: pathlib.Path,
    artifact_name: str,
    artifact_value: str,
    visualize_slice: Optional[pathlib.Path],
):
    """
    Executes python at PATH, saves the value ARTIFACT_VALUE with name ARTIFACT_NAME, and prints the sliced code.
    """
    # Create the code:
    code = path.read_text()
    code = code + generate_save_code(
        artifact_name, artifact_value, visualize_slice
    )

    # Run the code:
    db = RelationalLineaDB.from_environment()
    tracer = Tracer(db, SessionType.SCRIPT)
    # Redirect all stdout to stderr, so its not printed.
    with redirect_stdout(sys.stderr):

        transform(code, path, tracer)

    # Print the slice:
    # FIXME: weird indirection
    artifact = db.get_artifact_by_name(artifact_name)
    api_artifact = LineaArtifact(
        db=db,
        _execution_id=artifact.execution_id,
        _node_id=artifact.node_id,
        _session_id=artifact.node.session_id,
        _version=artifact.version,  # type:ignore
        name=artifact_name,
        date_created=artifact.date_created,  # type:ignore
    )
    # logger.info(api_artifact.get_code())
    print(api_artifact.get_code())


def generate_save_code(
    artifact_name: str,
    artifact_value: str,
    visualize_slice: Optional[pathlib.Path],
) -> str:

    return (
        "\nimport lineapy\n"
        # Save to a new variable first, so that if artifact value is composite, the slice of creating it
        # won't include the `lineapy.save` line.
        f"linea_artifact_value = {artifact_value}\n"
        f"linea_artifact = lineapy.save(linea_artifact_value, {repr(artifact_name)})\n"
    ) + (
        f"linea_artifact.visualize({repr(str(visualize_slice.resolve()))})"
        if visualize_slice
        else ""
    )


@linea_cli.command()
@click.option("--db-url", default=None, help=OVERRIDE_HELP_TEXT)
@click.option(
    "--slice",
    default=None,
    multiple=True,  # makes 'slice' variable a tuple
    help="Print the sliced code that this artifact depends on",
)
@click.option(
    "--export-slice",
    default=None,
    multiple=True,  # makes 'export-slice' variable a tuple
    help="Requires --slice. Export the sliced code that {slice} depends on to {export_slice}.py",
)
@click.option(
    "--export-slice-to-airflow-dag",
    "--airflow",
    default=None,
    help="Requires --slice. Export the sliced code from all slices to an Airflow DAG {export-slice-to-airflow-dag}.py",
)
@click.option(
    "--airflow-task-dependencies",
    default=None,
    help="Optional flag for --airflow. Specifies tasks dependencies in edgelist format [('a','b')] or graphlib format {'a':{'b'}}",
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
    "--visualize",
    help="Visualize the resulting graph with Graphviz",
    is_flag=True,
)
@click.option(
    "--arg",
    "-a",
    multiple=True,
    help="Args to pass to the underlying Python script",
)
@click.argument(
    "file_name",
    type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
)
def python(
    file_name: pathlib.Path,
    db_url: str,
    slice: List[str],  # cast tuple into list
    export_slice: List[str],  # cast tuple into list
    export_slice_to_airflow_dag: str,
    airflow_task_dependencies: str,
    print_source: bool,
    print_graph: bool,
    visualize: bool,
    arg: Iterable[str],
):
    set_custom_excepthook()
    tree = rich.tree.Tree(f"📄 {file_name}")

    db = RelationalLineaDB.from_environment(db_url)
    code = file_name.read_text()

    if print_source:
        tree.add(
            rich.console.Group(
                "Source code", rich.syntax.Syntax(code, "python")
            )
        )

    # Set the args to those passed in
    sys.argv = [str(file_name), *arg]
    # Change the working directory to that of the script,
    # To pick up relative data paths
    os.chdir(file_name.parent)

    tracer = Tracer(db, SessionType.SCRIPT)
    transform(code, file_name, tracer)

    send_lib_info_from_db(tracer.db, tracer.get_session_id())

    if visualize:
        from lineapy.visualizer import Visualizer

        Visualizer.for_public(tracer).render_pdf_file()

    if slice and not export_slice and not export_slice_to_airflow_dag:
        for _slice in slice:
            tree.add(
                rich.console.Group(
                    f"Slice of {repr(_slice)}",
                    rich.syntax.Syntax(tracer.slice(_slice), "python"),
                )
            )

    if export_slice:
        if not slice:
            logger.error(
                "Please specify --slice. It is required for --export-slice"
            )
            exit(1)
        for _slice, _export_slice in zip(slice, export_slice):
            full_code = tracer.slice(_slice)
            pathlib.Path(f"{_export_slice}.py").write_text(full_code)

    if export_slice_to_airflow_dag:
        if not slice:
            logger.error(
                "Please specify --slice. It is required for --export-slice-to-airflow-dag"
            )
            exit(1)

        ap = AirflowPlugin(db, tracer.tracer_context.get_session_id())
        ap.sliced_airflow_dag(
            slice,
            export_slice_to_airflow_dag,
            ast.literal_eval(airflow_task_dependencies),
        )

    db.close()
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


@linea_cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("jupyter_args", nargs=-1, type=click.UNPROCESSED)
def jupyter(jupyter_args):
    # Note that Jupyter wraps around iPython, which takes care of the lib sending
    setup_ipython_dir()
    res = subprocess.run(["jupyter", *jupyter_args])
    sys.exit(res.returncode)


@linea_cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("ipython_args", nargs=-1, type=click.UNPROCESSED)
def ipython(ipython_args):
    setup_ipython_dir()
    res = subprocess.run(["ipython", *ipython_args])
    sys.exit(res.returncode)


@linea_cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("jupytext_args", nargs=-1, type=click.UNPROCESSED)
def jupytext(jupytext_args):
    setup_ipython_dir()
    res = subprocess.run(["jupytext", *jupytext_args])
    sys.exit(res.returncode)


def setup_ipython_dir() -> None:
    """
    Set the ipython directory to include the lineapy extension by default
    """
    ipython_dir_name = tempfile.mkdtemp()
    # Make a default profile with the extension added to the ipython and kernel
    # configs
    profile_dir = pathlib.Path(ipython_dir_name) / "profile_default"
    profile_dir.mkdir()
    settings = 'c.InteractiveShellApp.extensions = ["lineapy"]'
    (profile_dir / "ipython_config.py").write_text(settings)
    (profile_dir / "ipython_kernel_config.py").write_text(settings)

    os.environ["IPYTHONDIR"] = ipython_dir_name


@linea_cli.group("annotate")
def annotations():
    """
    The annotate command can be used to import custom annotation sources
    into LineaPy. It can be used to add a source, list all sources,
    delete a source, and validate all sources.
    """
    pass


def validate_annotations_path(ctx, param, value: pathlib.Path):
    if value.suffix != ".yaml":
        raise click.BadParameter(
            f"Invalid path '{str(value)}'\n" + "path must be a yaml file"
        )
    if not value.exists():
        raise click.BadParameter(
            f"Invalid path '{str(value)}'\n"
            + "path must be to an existing yaml file"
        )
    return value


def remove_annotations_file_extension(filename: str) -> str:
    """
    Remove '.annotations.yaml' or '.yaml'.
    """
    filename = filename.replace(" ", "")
    for ext_to_strip in (".yaml", ".annotations"):
        name, ext = os.path.splitext(filename)
        if ext == ext_to_strip:
            filename = name
    return filename


@annotations.command("add")
@click.argument(
    "path",
    type=click.Path(dir_okay=False, path_type=pathlib.Path),
    callback=validate_annotations_path,
)
@click.option(
    "--name",
    "-n",
    default=None,
    help="What to name source. Input file name is used as default",
    type=str,
)
def add(path: pathlib.Path, name: str):
    """
    Import user-defined function annotations into Lineapy.

    This command copies the yaml file whose path is provided by the user into the user's .lineapy directory to allow Lineapy to manage it.
    """

    # validate that source is in correct format before importing
    try:
        invalid_specs = validate_spec(path)
        if len(invalid_specs) > 0:
            for invalid_spec in invalid_specs:
                logger.error(f"Invalid item {invalid_spec}")
            exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Unable to parse yaml file\n{e}")
        exit(1)

    # calculate name of new annotation source
    name = name or path.stem
    name = remove_annotations_file_extension(name)
    name = slugify(name)

    annotate_folder = custom_annotations_folder()

    # Path to copy destination in user's .lineapy directory
    destination_file = (
        annotate_folder / (name + CUSTOM_ANNOTATIONS_EXTENSION_NAME)
    ).resolve()
    print(f"Creating annotation source {name} at {destination_file}")

    # Copy annotation file to destinatiion
    try:
        shutil.copyfile(path, destination_file)
    except IOError as e:
        logger.error(
            f"Failed to copy file from {path} to {destination_file}.\n{str(e)}"
        )
        sys.exit(1)


@annotations.command("list")
def list():
    """
    Lists full paths to all imported annotation sources.
    """
    wildcard_path = os.path.join(
        custom_annotations_folder().resolve(),
        "*" + CUSTOM_ANNOTATIONS_EXTENSION_NAME,
    )

    for annotation_path in glob.glob(wildcard_path):
        # display source name and path to .annotations.yaml file in .lineapy folder
        source_filename = os.path.basename(annotation_path)
        source_name = remove_annotations_file_extension(source_filename)
        print(f"{source_name}\t{annotation_path}")


@annotations.command("delete")
@click.option(
    "--name",
    "-n",
    required=True,
    help="Name of source to delete. Type `lineapy annotate list` to see all sources.",
    type=str,
)
def delete(name: str):
    """
    Deletes imported annotation source.
    """
    name = remove_annotations_file_extension(name)
    name += CUSTOM_ANNOTATIONS_EXTENSION_NAME

    delete_path = custom_annotations_folder() / name
    try:
        os.remove(delete_path)
    except IsADirectoryError as e:
        logger.error(
            f"{delete_path} must be the path to a file, not a directory\n{e}"
        )
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(
            f"{delete_path} not a valid path. Run 'lineapy annotations list' for valid resources."
        )
        sys.exit(1)


def validate_benchmark_path(ctx, param, value: pathlib.Path):
    if not value.suffix == ".ipynb":
        raise click.BadParameter("path must be a notebook")
    return value


@linea_cli.command()
@click.argument(
    "path",
    type=click.Path(dir_okay=False, path_type=pathlib.Path),
    callback=validate_benchmark_path,
)
@click.option("--n", default=3, help="Number of times to run each case.")
@click.option(
    "--skip-baseline",
    help="Only run with lineapy, skip benchmarking the baseline.",
    is_flag=True,
)
def benchmark(path: pathlib.Path, n: int, skip_baseline: bool):
    """
    Benchmarks running the notebook at PATH with lineapy versus with pure Python.
    Runs with and without lineapy REPETITIONS times.

    Prints the length of each run, and some statistics if they are meaningfully different.
    """
    console = Console()
    console.rule(f"[bold red]Benchmarking[/] {path}")

    with open(path) as f:
        notebook = nbformat.read(f, nbformat.NO_CONVERT)

    # Turn off tensorflow logging
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    os.chdir(path.parent)

    exec_proc = ExecutePreprocessor(timeout=None)

    if not skip_baseline:
        console.rule("[bold green]Running without lineapy")

        without_lineapy: List[float] = []
        with Progress() as progress:
            task = progress.add_task("Executing...", total=n + 1)
            for i in range(n + 1):
                progress.advance(task)
                with redirect_stdout(None):
                    with redirect_stderr(None):
                        start_time = perf_counter()
                        exec_proc.preprocess(notebook)
                        duration = perf_counter() - start_time
                first_run = i == 0
                progress.console.print(
                    f"{duration:.1f} seconds{' (discarding first run)' if first_run else '' }"
                )
                if not first_run:
                    without_lineapy.append(duration)
        rich.print(f"Mean: {mean(without_lineapy):.1f} seconds")

    setup_ipython_dir()
    with_lineapy: List[float] = []
    console.rule("[bold green]Running with lineapy")

    with Progress() as progress:
        task = progress.add_task("Executing...", total=n)
        for _ in range(n):
            progress.advance(task)
            with redirect_stdout(None):
                with redirect_stderr(None):
                    start_time = perf_counter()
                    exec_proc.preprocess(notebook)
                    duration = perf_counter() - start_time
            progress.console.print(f"{duration:.1f} seconds")
            with_lineapy.append(duration)
    rich.print(f"Mean: {mean(with_lineapy):.1f} seconds")

    if not skip_baseline:

        console.rule("[bold blue]Analyzing")

        change = distribution_change(
            without_lineapy, with_lineapy, confidence_interval=0.90
        )
        rich.print(f"Lineapy is {str(change)}")


if __name__ == "__main__":
    linea_cli()
