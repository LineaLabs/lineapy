from pathlib import Path
from typing import Optional

from black import FileMode, format_str
from jinja2 import Environment, FileSystemLoader

import lineapy
from lineapy.config import linea_folder
from lineapy.graph_reader.program_slice import (
    get_program_slice,
    split_code_blocks,
)
from lineapy.instrumentation.tracer import Tracer


def sliced_aiflow_dag(tracer: Tracer, slice_name: str, func_name: str) -> str:
    """
    Returns a an Airflow DAG of the sliced code.

    :param tracer: the tracer object.
    :param slice_name: name of the artifacts to get the code slice for.
    :return: string containing the code of the Airflow DAG running this slice
    """
    artifact = tracer.db.get_artifact_by_name(slice_name)
    artifact_var = tracer.slice_var_name(artifact)
    if not artifact_var:
        return "Unable to extract the slice"
    slice_code = get_program_slice(tracer.graph, [artifact.node_id])
    return slice_to_airflow(
        slice_code,
        func_name,
        Path(tracer.session_context.working_directory),
        artifact_var,
    )


def slice_to_airflow(
    sliced_code: str,
    func_name: str,
    working_directory: Path,
    variable: Optional[str] = "",
) -> str:
    """
    Transforms sliced code into airflow code.

    If the variable is passed in, this will be printed at the end of the airflow block.
    """

    working_dir_str = repr(
        str(working_directory.relative_to((linea_folder() / "..").resolve()))
    )

    templateLoader = FileSystemLoader(
        searchpath=str(
            (Path(lineapy.__file__) / "../plugins/jinja_templates").resolve()
        )
    )
    templateEnv = Environment(loader=templateLoader)

    AIRFLOW_IMPORTS_TEMPLATE = templateEnv.get_template("imports.jinja")

    AIRFLOW_DAG_TEMPLATE = templateEnv.get_template("dag.jinja")

    AIRFLOW_TASK_TEMPLATE = templateEnv.get_template("task.jinja")

    AIRFLOW_FULL_TEMPLATE = templateEnv.get_template("full.jinja")

    # We split the code in import and code blocks and join them to full code test
    import_block, code_block, main_block = split_code_blocks(
        sliced_code, func_name
    )

    full_code = AIRFLOW_FULL_TEMPLATE.render(
        import_block=import_block,
        airflow_import_block=AIRFLOW_IMPORTS_TEMPLATE.render(),
        working_dir_str=working_dir_str,
        code_block=code_block,
        variable=variable,
        airflow_dag_block=AIRFLOW_DAG_TEMPLATE.render(DAG_NAME=func_name),
        airflow_task_block=AIRFLOW_TASK_TEMPLATE.render(TASK_NAME=func_name),
    )
    # Black lint
    black_mode = FileMode()
    black_mode.line_length = 79
    full_code = format_str(full_code, mode=black_mode)
    return full_code
