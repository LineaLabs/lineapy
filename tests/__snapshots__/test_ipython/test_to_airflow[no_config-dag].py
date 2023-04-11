import pathlib
import pickle

import a_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def task_a():

    a = a_module.get_a()

    if not pathlib.Path("/tmp").joinpath("").exists():
        pathlib.Path("/tmp").joinpath("").mkdir()
    pickle.dump(a, open("/tmp//variable_a.pickle", "wb"))


def task_setup():

    pickle_folder = pathlib.Path("/tmp").joinpath("")
    if not pickle_folder.exists():
        pickle_folder.mkdir()


def task_teardown():

    pickle_files = pathlib.Path("/tmp").joinpath("").glob("*.pickle")
    for f in pickle_files:
        f.unlink()


default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
}

with DAG(
    dag_id="a_dag",
    schedule_interval="*/15 * * * *",
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
) as dag:

    a = PythonOperator(
        task_id="a_task",
        python_callable=task_a,
    )

    setup = PythonOperator(
        task_id="setup_task",
        python_callable=task_setup,
    )

    teardown = PythonOperator(
        task_id="teardown_task",
        python_callable=task_teardown,
    )

    a >> teardown

    setup >> a
