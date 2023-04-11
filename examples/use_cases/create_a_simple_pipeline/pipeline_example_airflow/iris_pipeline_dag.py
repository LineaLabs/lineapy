import pathlib
import pickle

import iris_pipeline_module
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


def task_iris_preprocessed(url):

    url = str(url)

    df = iris_pipeline_module.get_iris_preprocessed(url)

    if not pathlib.Path("/tmp").joinpath("").exists():
        pathlib.Path("/tmp").joinpath("").mkdir()
    pickle.dump(df, open("/tmp//variable_df.pickle", "wb"))


def task_split_samples_for_artifact_iris_model_and_downstream(random_state, test_size):

    random_state = int(random_state)

    test_size = float(test_size)

    df = pickle.load(open("/tmp//variable_df.pickle", "rb"))

    split_samples = (
        iris_pipeline_module.get_split_samples_for_artifact_iris_model_and_downstream(
            df, random_state, test_size
        )
    )

    if not pathlib.Path("/tmp").joinpath("").exists():
        pathlib.Path("/tmp").joinpath("").mkdir()
    pickle.dump(split_samples, open("/tmp//variable_split_samples.pickle", "wb"))


def task_iris_model():

    split_samples = pickle.load(open("/tmp//variable_split_samples.pickle", "rb"))

    mod = iris_pipeline_module.get_iris_model(split_samples)

    if not pathlib.Path("/tmp").joinpath("").exists():
        pathlib.Path("/tmp").joinpath("").mkdir()
    pickle.dump(mod, open("/tmp//variable_mod.pickle", "wb"))


def task_iris_model_evaluation():

    mod = pickle.load(open("/tmp//variable_mod.pickle", "rb"))

    split_samples = pickle.load(open("/tmp//variable_split_samples.pickle", "rb"))

    mod_eval_test = iris_pipeline_module.get_iris_model_evaluation(mod, split_samples)

    if not pathlib.Path("/tmp").joinpath("").exists():
        pathlib.Path("/tmp").joinpath("").mkdir()
    pickle.dump(mod_eval_test, open("/tmp//variable_mod_eval_test.pickle", "wb"))


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
    "params": {
        "url": "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
        "test_size": 0.33,
        "random_state": 42,
    },
}

with DAG(
    dag_id="iris_pipeline_dag",
    schedule_interval="*/15 * * * *",
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
) as dag:

    iris_preprocessed = PythonOperator(
        task_id="iris_preprocessed_task",
        python_callable=task_iris_preprocessed,
        op_kwargs={"url": "{{ params.url }}"},
    )

    split_samples_for_artifact_iris_model_and_downstream = PythonOperator(
        task_id="split_samples_for_artifact_iris_model_and_downstream_task",
        python_callable=task_split_samples_for_artifact_iris_model_and_downstream,
        op_kwargs={
            "random_state": "{{ params.random_state }}",
            "test_size": "{{ params.test_size }}",
        },
    )

    iris_model = PythonOperator(
        task_id="iris_model_task",
        python_callable=task_iris_model,
    )

    iris_model_evaluation = PythonOperator(
        task_id="iris_model_evaluation_task",
        python_callable=task_iris_model_evaluation,
    )

    setup = PythonOperator(
        task_id="setup_task",
        python_callable=task_setup,
    )

    teardown = PythonOperator(
        task_id="teardown_task",
        python_callable=task_teardown,
    )

    iris_model >> iris_model_evaluation

    iris_model_evaluation >> teardown

    iris_preprocessed >> split_samples_for_artifact_iris_model_and_downstream

    setup >> iris_preprocessed

    split_samples_for_artifact_iris_model_and_downstream >> iris_model

    split_samples_for_artifact_iris_model_and_downstream >> iris_model_evaluation
