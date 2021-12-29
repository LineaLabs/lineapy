from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

import lineapy
from lineapy.config import linea_folder
from lineapy.graph_reader.program_slice import split_code_blocks
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils import prettify


def sliced_aiflow_dag(
    tracer: Tracer,
    slice_names: List[str],
    func_name: str,
    airflow_task_dependencies: str,
) -> str:
    """
    Returns a an Airflow DAG of the sliced code.

    :param tracer: the tracer object.
    :param airflow_task_dependencies: task dependencies as adjacency list,
                    i.e. "[['p value'], ['y']]" or "[['p value', 'x'], ['y']]"
                    This translates to "sliced_housing_dag_p >> sliced_housing_dag_y"
                    and "sliced_housing_dag_p,sliced_housing_dag_x >> sliced_housing_dag_y".
                    Here "sliced_housing_dag_p" and "sliced_housing_dag_x" are independent tasks
                    and "sliced_housing_dag_y" depends on them.
    :param func_name: name of the DAG and corresponding functions and task prefixes,
                    i.e. "sliced_housing_dag"
    :return: string containing the code of the Airflow DAG running this slice
    """

    artifacts_name = {}
    artifacts_code = {}
    for slice_name in slice_names:
        artifact_var = tracer.artifact_var_name(slice_name)
        slice_code = tracer.slice(slice_name)
        artifacts_code[artifact_var] = slice_code
        artifacts_name[slice_name] = artifact_var

    task_dependencies = (
        eval(airflow_task_dependencies.replace("\\", ""))
        if airflow_task_dependencies
        else []
    )

    def _parallel_tasks(leaf: List[str]):
        # join parallel tasks in comma separated string per Airflow conventions
        # append func_name to each artifact variable
        return ",".join(
            [f"{func_name}_{artifacts_name[node]}" for node in leaf]
        )

    # join sequential tasks in >> separated string per Airflow conventions
    task_dependencies_str = (
        " >> ".join(map(_parallel_tasks, task_dependencies))
        if task_dependencies
        else ""
    )
    return to_airflow(
        artifacts_code,
        func_name,
        Path(tracer.session_context.working_directory),
        task_dependencies_str,
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
    return prettify(full_code)
