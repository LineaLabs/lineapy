from pathlib import Path
from typing import Dict, List

import isort
from jinja2 import Environment, FileSystemLoader

import lineapy
from lineapy.graph_reader.program_slice import split_code_blocks
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils.config import linea_folder
from lineapy.utils.utils import prettify


def sliced_aiflow_dag(
    tracer: Tracer,
    slice_names: List[str],
    func_name: str,
    airflow_task_dependencies: str,
) -> str:
    """
    Returns a an Airflow DAG of the sliced code.

    :param tracer: the tracer object.
    :param slice_names: list of slice nemes to be used as tasks.
    :param func_name: name of the DAG and corresponding functions and task prefixes,
    i.e. "sliced_housing_dag"
    :param airflow_task_dependencies: task dependencies in Airflow format,
    i.e. "'p value' >> 'y'" or "'p value', 'x' >> 'y'". Put slice names under single quotes.
    This translates to "sliced_housing_dag_p >> sliced_housing_dag_y"
    and "sliced_housing_dag_p,sliced_housing_dag_x >> sliced_housing_dag_y".
    Here "sliced_housing_dag_p" and "sliced_housing_dag_x" are independent tasks
    and "sliced_housing_dag_y" depends on them.
    :return: string containing the code of the Airflow DAG running this slice
    """

    # Remove quotes
    airflow_task_dependencies = airflow_task_dependencies.replace("\\'", "")
    airflow_task_dependencies = airflow_task_dependencies.replace("'", "")

    artifacts_code = {}
    for slice_name in slice_names:
        artifact_var = tracer.artifact_var_name(slice_name)
        slice_code = tracer.slice(slice_name)
        artifacts_code[artifact_var] = slice_code
        # "'p value' >> 'y'" needs to be replaced by "sliced_housing_dag_p >> sliced_housing_dag_y"
        airflow_task_dependencies = airflow_task_dependencies.replace(
            slice_name, f"{func_name}_{artifact_var}"
        )

    return to_airflow(
        artifacts_code,
        func_name,
        Path(tracer.session_context.working_directory),
        airflow_task_dependencies,
    )


def to_airflow(
    artifacts_code: Dict[str, str],
    func_name: str,
    working_directory: Path,
    task_dependencies: str = "",
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
    # Sort imports and move them to the top
    full_code = isort.code(full_code, float_to_top=True, profile="black")
    return prettify(full_code)
