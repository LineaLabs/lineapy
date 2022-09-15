import pathlib
import pickle

import airflow_pipeline_a_b0_inputpar_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def dag_setup():
    pickle_folder = pathlib.Path("/tmp").joinpath("airflow_pipeline_a_b0_inputpar")
    if not pickle_folder.exists():
        pickle_folder.mkdir()


def dag_teardown():
    pickle_files = (
        pathlib.Path("/tmp").joinpath("airflow_pipeline_a_b0_inputpar").glob("*.pickle")
    )
    for f in pickle_files:
        f.unlink()


def task_b0(b0):

    b0 = int(b0)

    b0 = airflow_pipeline_a_b0_inputpar_module.get_b0(b0)

    pickle.dump(
        b0, open("/tmp/airflow_pipeline_a_b0_inputpar/variable_b0.pickle", "wb")
    )


def task_a():

    b0 = pickle.load(
        open("/tmp/airflow_pipeline_a_b0_inputpar/variable_b0.pickle", "rb")
    )

    a = airflow_pipeline_a_b0_inputpar_module.get_a(b0)

    pickle.dump(a, open("/tmp/airflow_pipeline_a_b0_inputpar/variable_a.pickle", "wb"))


default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
    "params": {"b0": 0},
}

with DAG(
    dag_id="airflow_pipeline_a_b0_inputpar_dag",
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

    b0 = PythonOperator(
        task_id="b0_task",
        python_callable=task_b0,
        op_kwargs={"b0": "{{ params.b0 }}"},
    )

    a = PythonOperator(
        task_id="a_task",
        python_callable=task_a,
    )

    b0 >> a

    setup >> b0

    a >> teardown
