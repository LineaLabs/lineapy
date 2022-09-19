import pathlib
import pickle

import airflow_pipeline_two_input_parameter_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def dag_setup():
    pickle_folder = pathlib.Path("/tmp").joinpath(
        "airflow_pipeline_two_input_parameter"
    )
    if not pickle_folder.exists():
        pickle_folder.mkdir()


def dag_teardown():
    pickle_files = (
        pathlib.Path("/tmp")
        .joinpath("airflow_pipeline_two_input_parameter")
        .glob("*.pickle")
    )
    for f in pickle_files:
        f.unlink()


def task_pn(n, p):

    n = int(n)

    p = str(p)

    pn = airflow_pipeline_two_input_parameter_module.get_pn(n, p)

    pickle.dump(
        pn, open("/tmp/airflow_pipeline_two_input_parameter/variable_pn.pickle", "wb")
    )


default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
    "params": {"p": "p", "n": 5},
}

with DAG(
    dag_id="airflow_pipeline_two_input_parameter_dag",
    schedule_interval="*/15 * * * *",
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
) as dag:

    setup = PythonOperator(
        task_id="dag_setup",
        python_callable=dag_setup,
    )

    teardown = PythonOperator(
        task_id="dag_teardown",
        python_callable=dag_teardown,
    )

    pn = PythonOperator(
        task_id="pn_task",
        python_callable=task_pn,
        op_kwargs={"n": "{{ params.n }}", "p": "{{ params.p }}"},
    )

    setup >> pn

    pn >> teardown
