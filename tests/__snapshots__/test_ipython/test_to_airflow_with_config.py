import os

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

if "." not in os.getcwd():
    os.chdir(".")


def a_a():
    a = [1, 2, 3]


default_dag_args = {"owner": "airflow", "retries": 1, "start_date": days_ago(1)}

dag = DAG(
    dag_id="a_dag",
    schedule_interval="*/30 * * * *",
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
)


a_a = PythonOperator(
    dag=dag,
    task_id="a_a_task",
    python_callable=a_a,
)
