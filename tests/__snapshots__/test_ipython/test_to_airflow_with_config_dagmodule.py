import a_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

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

    run_session_including_a = PythonOperator(
        task_id="run_session_including_a_task",
        python_callable=a_module.run_session_including_a,
    )
