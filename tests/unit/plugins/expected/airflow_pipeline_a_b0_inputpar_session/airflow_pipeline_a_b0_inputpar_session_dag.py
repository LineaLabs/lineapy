import pathlib
import pickle

import airflow_pipeline_a_b0_inputpar_session_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def dag_setup():
    pickle_folder = pathlib.Path("/tmp").joinpath(
        "airflow_pipeline_a_b0_inputpar_session"
    )
    if not pickle_folder.exists():
        pickle_folder.mkdir()


def dag_teardown():
    pickle_files = (
        pathlib.Path("/tmp")
        .joinpath("airflow_pipeline_a_b0_inputpar_session")
        .glob("*.pickle")
    )
    for f in pickle_files:
        f.unlink()


def task_run_session_including_b0(b0):

    b0 = int(b0)

    artifacts = airflow_pipeline_a_b0_inputpar_session_module.run_session_including_b0(
        b0
    )

    pickle.dump(
        artifacts["b0"],
        open("/tmp/airflow_pipeline_a_b0_inputpar_session/artifact_b0.pickle", "wb"),
    )

    pickle.dump(
        artifacts["a"],
        open("/tmp/airflow_pipeline_a_b0_inputpar_session/artifact_a.pickle", "wb"),
    )


default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
    "params": {"b0": 0},
}

with DAG(
    dag_id="airflow_pipeline_a_b0_inputpar_session_dag",
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

    run_session_including_b0 = PythonOperator(
        task_id="run_session_including_b0_task",
        python_callable=task_run_session_including_b0,
        op_kwargs={"b0": "{{ params.b0 }}"},
    )

    setup >> run_session_including_b0

    run_session_including_b0 >> teardown
