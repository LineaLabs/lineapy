from os import chdir

import pandas as pd
from sklearn.ensemble import RandomForestClassifier


from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator


chdir("tests")


def sliced_housing_dag_p():
    assets = pd.read_csv("ames_train_cleaned.csv")

    def is_new(col):
        return col > 1970

    assets["is_new"] = is_new(assets["Year_Built"])
    clf = RandomForestClassifier(random_state=0)
    y = assets["is_new"]
    x = assets[["SalePrice", "Lot_Area", "Garage_Area"]]
    clf.fit(x, y)
    p = clf.predict([[100 * 1000, 10, 4]])


default_dag_args = {"owner": "airflow", "retries": 2, "start_date": days_ago(1)}

dag = DAG(
    dag_id="sliced_housing_dag_dag",
    schedule_interval="*/15 * * * *",
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
)


sliced_housing_dag_p = PythonOperator(
    dag=dag,
    task_id="sliced_housing_dag_p_task",
    python_callable=sliced_housing_dag_p,
)
