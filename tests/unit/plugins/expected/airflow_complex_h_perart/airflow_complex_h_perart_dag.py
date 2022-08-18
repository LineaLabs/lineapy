import pathlib
import pickle

import airflow_complex_h_perart_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def task_setup():
    pickle_folder = pathlib.Path("/tmp").joinpath("airflow_complex_h_perart")
    if not pickle_folder.exists():
        pickle_folder.mkdir()


def task_teardown():
    pickle_files = (
        pathlib.Path("/tmp").joinpath("airflow_complex_h_perart").glob("*.pickle")
    )
    for f in pickle_files:
        f.unlink()


def task_a_c_for_artifact_f_and_downstream():

    a, c = airflow_complex_h_perart_module.get_a_c_for_artifact_f_and_downstream()

    pickle.dump(a, open("/tmp/airflow_complex_h_perart/variable_a.pickle", "wb"))

    pickle.dump(c, open("/tmp/airflow_complex_h_perart/variable_c.pickle", "wb"))


def task_f():

    c = pickle.load(open("/tmp/airflow_complex_h_perart/variable_c.pickle", "rb"))

    f = airflow_complex_h_perart_module.get_f(c)

    pickle.dump(f, open("/tmp/airflow_complex_h_perart/variable_f.pickle", "wb"))


def task_h():

    a = pickle.load(open("/tmp/airflow_complex_h_perart/variable_a.pickle", "rb"))

    c = pickle.load(open("/tmp/airflow_complex_h_perart/variable_c.pickle", "rb"))

    h = airflow_complex_h_perart_module.get_h(a, c)

    pickle.dump(h, open("/tmp/airflow_complex_h_perart/variable_h.pickle", "wb"))


default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
}

with DAG(
    dag_id="airflow_complex_h_perart_dag",
    schedule_interval="*/15 * * * *",
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
) as dag:

    setup = PythonOperator(
        task_id="task_setup",
        python_callable=task_setup,
    )

    teardown = PythonOperator(
        task_id="task_teardown",
        python_callable=task_teardown,
    )

    a_c_for_artifact_f_and_downstream = PythonOperator(
        task_id="a_c_for_artifact_f_and_downstream_task",
        python_callable=task_a_c_for_artifact_f_and_downstream,
    )

    f = PythonOperator(
        task_id="f_task",
        python_callable=task_f,
    )

    h = PythonOperator(
        task_id="h_task",
        python_callable=task_h,
    )

    a_c_for_artifact_f_and_downstream >> f

    f >> h

    setup >> a_c_for_artifact_f_and_downstream

    h >> teardown
