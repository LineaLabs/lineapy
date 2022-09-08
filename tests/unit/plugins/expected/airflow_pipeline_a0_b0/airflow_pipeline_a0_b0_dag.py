import pathlib
import pickle

import airflow_pipeline_a0_b0_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def dag_setup():
    pickle_folder = pathlib.Path("/tmp").joinpath("airflow_pipeline_a0_b0")
    if not pickle_folder.exists():
        pickle_folder.mkdir()


def dag_teardown():
    pickle_files = (
        pathlib.Path("/tmp").joinpath("airflow_pipeline_a0_b0").glob("*.pickle")
    )
    for f in pickle_files:
        f.unlink()


def task_a0():

    a0 = airflow_pipeline_a0_b0_module.get_a0()

    pickle.dump(a0, open("/tmp/airflow_pipeline_a0_b0/variable_a0.pickle", "wb"))


def task_b0():

    b0 = airflow_pipeline_a0_b0_module.get_b0()

    pickle.dump(b0, open("/tmp/airflow_pipeline_a0_b0/variable_b0.pickle", "wb"))


default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
}

with DAG(
    dag_id="airflow_pipeline_a0_b0_dag",
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

    a0 = PythonOperator(
        task_id="a0_task",
        python_callable=task_a0,
    )

    b0 = PythonOperator(
        task_id="b0_task",
        python_callable=task_b0,
    )

    a0 >> b0

    setup >> a0

    b0 >> teardown
