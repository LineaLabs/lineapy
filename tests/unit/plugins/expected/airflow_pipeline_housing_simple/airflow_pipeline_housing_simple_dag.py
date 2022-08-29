import pathlib
import pickle

import airflow_pipeline_housing_simple_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def dag_setup():
    pickle_folder = pathlib.Path("/tmp").joinpath("airflow_pipeline_housing_simple")
    if not pickle_folder.exists():
        pickle_folder.mkdir()


def dag_teardown():
    pickle_files = (
        pathlib.Path("/tmp")
        .joinpath("airflow_pipeline_housing_simple")
        .glob("*.pickle")
    )
    for f in pickle_files:
        f.unlink()


def task_p_value():

    p = airflow_pipeline_housing_simple_module.get_p_value()

    pickle.dump(p, open("/tmp/airflow_pipeline_housing_simple/variable_p.pickle", "wb"))


default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
}

with DAG(
    dag_id="airflow_pipeline_housing_simple_dag",
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

    p_value = PythonOperator(
        task_id="p_value_task",
        python_callable=task_p_value,
    )

    setup >> p_value

    p_value >> teardown
