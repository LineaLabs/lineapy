import pathlib
import pickle

import airflow_pipeline_housing_w_dependencies_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def dag_setup():
    pickle_folder = pathlib.Path("/tmp").joinpath(
        "airflow_pipeline_housing_w_dependencies"
    )
    if not pickle_folder.exists():
        pickle_folder.mkdir()


def dag_teardown():
    pickle_files = (
        pathlib.Path("/tmp")
        .joinpath("airflow_pipeline_housing_w_dependencies")
        .glob("*.pickle")
    )
    for f in pickle_files:
        f.unlink()


def task_assets_for_artifact_y_and_downstream():

    assets = (
        airflow_pipeline_housing_w_dependencies_module.get_assets_for_artifact_y_and_downstream()
    )

    pickle.dump(
        assets,
        open(
            "/tmp/airflow_pipeline_housing_w_dependencies/variable_assets.pickle", "wb"
        ),
    )


def task_y():

    assets = pickle.load(
        open(
            "/tmp/airflow_pipeline_housing_w_dependencies/variable_assets.pickle", "rb"
        )
    )

    y = airflow_pipeline_housing_w_dependencies_module.get_y(assets)

    pickle.dump(
        y, open("/tmp/airflow_pipeline_housing_w_dependencies/variable_y.pickle", "wb")
    )


def task_p_value():

    assets = pickle.load(
        open(
            "/tmp/airflow_pipeline_housing_w_dependencies/variable_assets.pickle", "rb"
        )
    )

    y = pickle.load(
        open("/tmp/airflow_pipeline_housing_w_dependencies/variable_y.pickle", "rb")
    )

    p = airflow_pipeline_housing_w_dependencies_module.get_p_value(assets, y)

    pickle.dump(
        p, open("/tmp/airflow_pipeline_housing_w_dependencies/variable_p.pickle", "wb")
    )


default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
}

with DAG(
    dag_id="airflow_pipeline_housing_w_dependencies_dag",
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

    assets_for_artifact_y_and_downstream = PythonOperator(
        task_id="assets_for_artifact_y_and_downstream_task",
        python_callable=task_assets_for_artifact_y_and_downstream,
    )

    y = PythonOperator(
        task_id="y_task",
        python_callable=task_y,
    )

    p_value = PythonOperator(
        task_id="p_value_task",
        python_callable=task_p_value,
    )

    assets_for_artifact_y_and_downstream >> y

    y >> p_value

    setup >> assets_for_artifact_y_and_downstream

    p_value >> teardown
