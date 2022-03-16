import os

import sliced_housing_multiple_w_dependencies
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

if "tests" not in os.getcwd():
    os.chdir("tests")


default_dag_args = {"owner": "airflow", "retries": 2, "start_date": days_ago(1)}

dag = DAG(
    dag_id="sliced_housing_multiple_w_dependencies_dag",
    schedule_interval="*/15 * * * *",
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
)


p_value = PythonOperator(
    dag=dag,
    task_id="p_value_task",
    python_callable=sliced_housing_multiple_w_dependencies.p_value,
)

y = PythonOperator(
    dag=dag,
    task_id="y_task",
    python_callable=sliced_housing_multiple_w_dependencies.y,
)


p_value >> y
