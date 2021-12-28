from pathlib import Path
from typing import Dict, List, Optional

import isort
from black import FileMode, format_str
from jinja2 import Environment, FileSystemLoader

import lineapy
from lineapy.config import linea_folder
from lineapy.graph_reader.program_slice import (
    get_program_slice,
    split_code_blocks,
)
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils import prettify


def sliced_aiflow_dag(
    tracer: Tracer,
    slice_names: List[str],
    task_dependencies: str,
    func_name: str,
) -> str:
    """
    Returns a an Airflow DAG of the sliced code.

    :param tracer: the tracer object.
    :param slice_name: name of the artifacts to get the code slice for.
    :return: string containing the code of the Airflow DAG running this slice
    """
    artifacts_code = {}
    for slice_name in slice_names:
        artifact = tracer.db.get_artifact_by_name(slice_name)
        artifact_var = tracer.artifact_var_name(artifact)
        if not artifact_var:
            return "Unable to extract the slice"
        slice_code = get_program_slice(tracer.graph, [artifact.node_id])
        artifacts_code[artifact_var] = slice_code
    return to_airflow(
        artifacts_code,
        task_dependencies,
        func_name,
        Path(tracer.session_context.working_directory),
    )


def to_airflow(
    artifacts_code: Dict[str, str],
    task_dependencies: str,
    func_name: str,
    working_directory: Path,
) -> str:
    """
    Transforms sliced code into airflow code.
    """

    working_dir_str = repr(
        str(working_directory.relative_to((linea_folder() / "..").resolve()))
    )

    template_loader = FileSystemLoader(
        searchpath=str(
            (Path(lineapy.__file__) / "../plugins/jinja_templates").resolve()
        )
    )
    template_env = Environment(loader=template_loader)

    AIRFLOW_DAG_TEMPLATE = template_env.get_template("airflow_dag.jinja")

    _import_blocks = []
    _code_blocks = []
    _task_names = []
    for artifact_name, sliced_code in artifacts_code.items():
        # We split the code in import and code blocks and form a faunction that calculates the artifact
        artifact_func_name = f"{func_name}_{artifact_name}"
        _import_block, _code_block, _ = split_code_blocks(
            sliced_code, artifact_func_name
        )
        _import_blocks.append(_import_block)
        _code_blocks.append(_code_block)
        _task_names.append(artifact_func_name)

    full_code = AIRFLOW_DAG_TEMPLATE.render(
        import_blocks=_import_blocks,
        working_dir_str=working_dir_str,
        code_blocks=_code_blocks,
        DAG_NAME=func_name,
        tasks=_task_names,
        task_dependencies=task_dependencies,
    )
    return prettify(full_code)
