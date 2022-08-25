import airflow_pipeline_housing_multiple_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
}

with DAG(
    dag_id="airflow_pipeline_housing_multiple_dag",
    schedule_interval="*/15 * * * *",
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
) as dag:

    run_session_including_y = PythonOperator(
        task_id="run_session_including_y_task",
        python_callable=airflow_pipeline_housing_multiple_module.run_session_including_y,
    )
