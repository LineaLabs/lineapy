import pathlib
import pickle

import a_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def task_setup():

    pickle_folder = pathlib.Path("/tmp").joinpath("a")
    if not pickle_folder.exists():
        pickle_folder.mkdir()


def task_a():

    a = a_module.get_a()

    pickle.dump(a, open("/tmp/a/variable_a.pickle", "wb"))


def task_teardown():

    pickle_files = pathlib.Path("/tmp").joinpath("a").glob("*.pickle")
    for f in pickle_files:
        f.unlink()


default_dag_args = {
    "owner": "airflow",
    "retries": 1,
    "start_date": days_ago(1),
}

with DAG(
    dag_id="a_dag",
    schedule_interval="*/30 * * * *",
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
) as dag:

    setup = PythonOperator(
        task_id="setup_task",
        python_callable=task_setup,
    )

    a = PythonOperator(
        task_id="a_task",
        python_callable=task_a,
    )

    teardown = PythonOperator(
        task_id="teardown_task",
        python_callable=task_teardown,
    )

    setup >> a

    a >> teardown
