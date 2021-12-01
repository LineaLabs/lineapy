import os
import pickle
import textwrap
from importlib import import_module
from pathlib import Path
from typing import Optional

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from black import FileMode, format_str

from lineapy.config import linea_folder
from lineapy.graph_reader.program_slice import (
    get_program_slice,
    split_code_blocks,
)
from lineapy.instrumentation.tracer import Tracer

AIRFLOW_IMPORTS_TEMPLATE = """
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
"""

AIRFLOW_DAG_TEMPLATE = """
default_dag_args = {"owner": "airflow", "retries": 2, "start_date": days_ago(1)}

dag = DAG(
    dag_id="DAG_NAME_dag",
    schedule_interval="*/15 * * * *",  # Every 15 minutes
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
)
"""

AIRFLOW_TASK_TEMPLATE = """
TASK_NAME = PythonOperator(
    dag=dag, task_id=f"TASK_NAME_task", python_callable=TASK_NAME,
)
"""


def sliced_aiflow_dag(tracer: Tracer, slice_name: str, func_name: str) -> str:
    """
    Returns a an Airflow DAG of the sliced code.

    :param tracer: the tracer object.
    :param slice_name: name of the artifacts to get the code slice for.
    :return: string containing the code of the Airflow DAG running this slice
    """
    slice_code = tracer.sliced_func(slice_name, func_name + "_task")
    slice_to_airflow(slice_code, func_name)


def register_pickled_dag(dag, dag_folder_path=""):

    """
    registers (pushes) an airflow dag object to its dag folder, along with python script that
    can load the pickled dag into memory. name of the pickled dag and its reader py script will
    have have the dag as its name with a "auto_"

    Inputs:
    dag: an airflow dag object
    dag_folder_path='': If empty, pickled dag objects will be saved into
    airflow's default dag folder
    """

    dag_name = "".join(["auto_", dag.dag_id])

    if not dag_folder_path:
        dag_folder_path = "".join([os.environ["AIRFLOW_HOME"], "/dags/"])

    dag_pkl_name = "".join([dag_folder_path, dag_name, ".pkl"])
    dag_pyfile_name = "".join([dag_folder_path, dag_name, ".py"])

    with open(dag_pkl_name, "wb") as f:
        pickle.dump(dag, f)

    pyscript = """
    import pickle
    from airflow.models import DAG
    
    with open('{}', 'rb') as f:
        tmp_object = pickle.load(f)
        
    if isinstance(tmp_object,DAG):
            globals()['{}'] = tmp_object
    del tmp_object
    """
    pyscript = pyscript.format(dag_pkl_name, dag_name)
    dedented_pyscript = textwrap.dedent(pyscript).strip()

    with open(dag_pyfile_name, "w") as f:
        f.write(dedented_pyscript)


def slice_to_airflow(sliced_code: str, func_name: str) -> str:
    """
    Transforms sliced code into airflow code.
    """

    default_dag_args = {
        "owner": "airflow",
        "retries": 2,
        "start_date": days_ago(1),
    }

    dag = DAG(
        dag_id="DAG_NAME_dag",
        schedule_interval="*/15 * * * *",  # Every 15 minutes
        max_active_runs=1,
        catchup=False,
        default_args=default_dag_args,
    )

    with open(func_name + "_task.py", "wb") as f:
        f.write(sliced_code.encode("utf8"))
    func_callable = getattr(
        import_module(func_name + "_task"), func_name + "_task"
    )

    func_name_task = PythonOperator(
        dag=dag,
        task_id=f"{func_name}_task",
        python_callable=func_callable,
    )

    register_pickled_dag(dag)
