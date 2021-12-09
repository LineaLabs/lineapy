from pathlib import Path
from typing import Optional

from black import FileMode, format_str
from jinja2 import Template

from lineapy.config import linea_folder
from lineapy.graph_reader.program_slice import (
    get_program_slice,
    split_code_blocks,
)
from lineapy.instrumentation.tracer import Tracer

AIRFLOW_IMPORTS_TEMPLATE = Template(
    """
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
"""
)

AIRFLOW_DAG_TEMPLATE = Template(
    """
default_dag_args = {"owner": "airflow", "retries": 2, "start_date": days_ago(1)}

dag = DAG(
    dag_id="{{ DAG_NAME }}_dag",
    schedule_interval="*/15 * * * *",  # Every 15 minutes
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
)
"""
)

AIRFLOW_TASK_TEMPLATE = Template(
    """
{{ TASK_NAME }} = PythonOperator(
    dag=dag, task_id="{{ TASK_NAME }}_task", python_callable={{ TASK_NAME }},
)
"""
)

AIRFLOW_FULL_TEMPLATE = Template(
    """
from os import chdir
{{ import_block }}
{{ airflow_import_block }}

{# Change directory before executing to proper place #}
chdir({{ working_dir_str }})

{{ code_block }}
{% if variable != "" %}
\tprint({{ variable }})
{% endif %}
{# TODO What to do with artifact_var in a DAG? #}

{{ airflow_dag_block }}
{{ airflow_task_block }}
"""
)


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
    variable: Optional[str] = None,
) -> str:
    """
    Transforms sliced code into airflow code.

    If the variable is passed in, this will be printed at the end of the airflow block.
    """
    # We split the code in import and code blocks and join them to full code test
    import_block, code_block, main_block = split_code_blocks(
        sliced_code, func_name
    )

    working_dir_str = repr(
        str(working_directory.relative_to((linea_folder() / "..").resolve()))
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
