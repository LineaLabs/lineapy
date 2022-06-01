import ast
import glob
import json
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
import IPython
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
from lineapy.exceptions.excepthook import set_custom_excepthook
from lineapy.graph_reader.apis import LineaArtifact
from lineapy.instrumentation.tracer import Tracer
from lineapy.plugins.airflow import AirflowPlugin
from lineapy.plugins.utils import slugify
from lineapy.transformer.node_transformer import transform
from lineapy.utils.analytics import send_lib_info_from_db
from lineapy.utils.benchmarks import distribution_change
from lineapy.utils.config import (
    CONFIG_FILE_NAME,
    CUSTOM_ANNOTATIONS_EXTENSION_NAME,
    options,
)
from lineapy.utils.logging_config import configure_logging
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
    help="Print out logging for graph creation and execution.",
    is_flag=True,
)
@click.option(
    "--home-dir",
    type=click.Path(dir_okay=True, path_type=pathlib.Path),
    help="LineaPy home directory.",
)
@click.option(
    "--database-url",
    type=click.STRING,
    help="SQLAlchemy connection string for LineaPy database.",
)
@click.option(
    "--artifact-storage-dir",
    type=click.Path(dir_okay=True, path_type=pathlib.Path),
    help="LineaPy artifact directory.",
)
@click.option(
    "--customized-annotation-dir",
    type=click.Path(dir_okay=True, path_type=pathlib.Path),
    help="Customized annotation directory.",
)
@click.option(
    "--do-not-track",
    type=click.BOOL,
    help="Opt out for user analytics.",
    is_flag=True,
)
@click.option(
    "--logging-level",
    type=click.Choice(
        list(logging._nameToLevel.keys())
        + sorted([str(x) for x in set(logging._levelToName.keys())]),
        case_sensitive=False,
    ),
    help="Logging level for LineaPy.",
)
@click.option(
    "--logging-file",
    type=click.Path(dir_okay=False, path_type=pathlib.Path),
    help="Logging file",
)
def linea_cli(
    verbose: bool,
    home_dir: Optional[pathlib.Path],
    database_url: Optional[str],
    artifact_storage_dir: Optional[pathlib.Path],
    customized_annotation_dir: Optional[pathlib.Path],
    do_not_track: Optional[bool],
    logging_level: Optional[str],
    logging_file: Optional[pathlib.Path],
):
    """
    Pass all configuration to lineapy_config
    """
    args = [x for x in locals().keys()]

    # Set the logging env variable so its passed to subprocesses, like creating a jupyter kernel
    if verbose:
        options.set("LINEAPY_LOG_LEVEL", "DEBUG")

    configure_logging()

    for arg in args:
        if arg in options.__dict__.keys() and locals().get(arg) is not None:
            options.set(arg, locals().get(arg))

    options._set_defaults()


@linea_cli.command()
@click.option(
    "--output-file",
    type=click.Path(dir_okay=False, path_type=pathlib.Path),
    help="Output LineaPy config file",
)
def init(output_file: Optional[pathlib.Path]):
    """
    Create config file based on your desired output file path.
    If the file path is not specified, it will be at ``LINEAPY_HOME_DIR/CONFIG_FILE_NAME``

    For example,

        lineapy --home-dir=/lineapy init


    will generate a config file with ``home_dir='/lineapy'``
    """
    if output_file is None:
        output_file = pathlib.Path(options.home_dir).joinpath(CONFIG_FILE_NAME)

    with open(output_file, "w") as f:
        logging.info(f"Writing LineaPy config file to {output_file}")
        config = {
            k: str(v) for k, v in options.__dict__.items() if v is not None
        }
        json.dump(config, f)


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
    db = RelationalLineaDB.from_config(options)
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
    logger.info(api_artifact.get_code())


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
    db = RelationalLineaDB.from_config(options)
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
    logger.info(api_artifact.get_code())


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

    db = RelationalLineaDB.from_config(options)
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
    """Set the ipython directory to include the lineapy extension.

    If IPython configure files exist, we copy them to temp the folder and append
    a line to add lineapy into ``extra_extensions``. If they do not exist, we create
    new config files in the temp folder and add a line to specify ``extra_extensions``.
    """
    ipython_dir_name = tempfile.mkdtemp()
    # Make a default profile with the extension added to the ipython and kernel
    # configs
    profile_dir = pathlib.Path(ipython_dir_name) / "profile_default"
    profile_dir.mkdir()

    append_settings = (
        '\nc.InteractiveShellApp.extra_extensions.append("lineapy")'
    )
    write_settings = 'c.InteractiveShellApp.extra_extensions = ["lineapy"]'

    existing_profile_dir = pathlib.Path(
        IPython.paths.get_ipython_dir()
    ).joinpath("profile_default")

    for config_file in ["ipython_config.py", "ipython_kernel_config.py"]:
        if existing_profile_dir.joinpath(config_file).exists():
            logger.debug(
                f"Default {config_file} founded, append setting to this one."
            )
            shutil.copy(
                existing_profile_dir.joinpath(config_file),
                profile_dir.joinpath(config_file),
            )
            with open(profile_dir.joinpath(config_file), "a") as f:
                f.write(append_settings)
        else:
            logger.debug(
                f"No default {config_file} founded, create a new one."
            )
            profile_dir.joinpath(config_file).write_text(write_settings)

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

    annotate_folder = options.safe_get("customized_annotation_folder")

    # Path to copy destination in user's .lineapy directory
    destination_file = (
        pathlib.Path(annotate_folder)
        / (name + CUSTOM_ANNOTATIONS_EXTENSION_NAME)
    ).resolve()
    logger.info(f"Creating annotation source {name} at {destination_file}")

    # Copy annotation file to destination
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
        pathlib.Path(
            options.safe_get("customized_annotation_folder")
        ).resolve(),
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

    delete_path = pathlib.Path(
        options.safe_get("customized_annotation_folder")
    ).joinpath(name)
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
