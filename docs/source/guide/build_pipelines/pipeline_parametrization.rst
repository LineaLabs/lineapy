Parametrization
===============

.. include:: ../../snippets/slack_support.rstinc

Oftentimes, data scientists/engineers need to run the same pipeline with different parameters.
For instance, they may want to use a different data set for model training and/or prediction.
To produce a parametrized pipeline, we can use pipeline API's (optional) ``input_parameters`` argument.

As a concrete example, consider the :ref:`pipeline created in the Basics section <iris_pipeline_module>`,
where we got an "inflexible" pipeline that has the data source (``url``) as a fixed value:

.. code-block:: python
    :emphasize-lines: 8

    # ./output/pipeline_basics/iris_pipeline_module.py

    import pandas as pd
    from sklearn.linear_model import LinearRegression


    def get_iris_preprocessed():
        url = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
        df = pd.read_csv(url)
        color_map = {"Setosa": "green", "Versicolor": "blue", "Virginica": "red"}
        df["variety_color"] = df["variety"].map(color_map)
        df["d_versicolor"] = df["variety"].apply(lambda x: 1 if x == "Versicolor" else 0)
        df["d_virginica"] = df["variety"].apply(lambda x: 1 if x == "Virginica" else 0)
        return df

    [...]

    def run_session_including_iris_preprocessed():
        # Given multiple artifacts, we need to save each right after
        # its calculation to protect from any irrelevant downstream
        # mutations (e.g., inside other artifact calculations)
        import copy

        artifacts = dict()
        df = get_iris_preprocessed()
        artifacts["iris_preprocessed"] = copy.deepcopy(df)
        mod = get_iris_model(df)
        artifacts["iris_model"] = copy.deepcopy(mod)
        return artifacts

    [...]

    if __name__ == "__main__":
        # Edit this section to customize the behavior of artifacts
        artifacts = run_all_sessions()
        print(artifacts)

Instead, we can run

.. code-block:: python
   :emphasize-lines: 6

    # Build an Airflow pipeline using artifacts
    lineapy.to_pipeline(
        pipeline_name="iris_pipeline_parametrized",
        artifacts=["iris_preprocessed", "iris_model"],
        dependencies={"iris_model": {"iris_preprocessed"}},
        input_parameters=["url"],  # Specify variable(s) to parametrize
        output_dir="./output/pipeline_parametrization/",
        framework="AIRFLOW",
    )

to get a parametrized pipline, like so:

.. code-block:: python
   :emphasize-lines: 9, 20, 42

    # ./output/pipeline_parametrization/iris_pipeline_parametrized_module.py

    import argparse

    import pandas as pd
    from sklearn.linear_model import LinearRegression


    def get_iris_preprocessed(url):
        df = pd.read_csv(url)
        color_map = {"Setosa": "green", "Versicolor": "blue", "Virginica": "red"}
        df["variety_color"] = df["variety"].map(color_map)
        df["d_versicolor"] = df["variety"].apply(lambda x: 1 if x == "Versicolor" else 0)
        df["d_virginica"] = df["variety"].apply(lambda x: 1 if x == "Virginica" else 0)
        return df

    [...]

    def run_session_including_iris_preprocessed(
        url="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
    ):
        # Given multiple artifacts, we need to save each right after
        # its calculation to protect from any irrelevant downstream
        # mutations (e.g., inside other artifact calculations)
        import copy

        artifacts = dict()
        df = get_iris_preprocessed(url)
        artifacts["iris_preprocessed"] = copy.deepcopy(df)
        mod = get_iris_model(df)
        artifacts["iris_model"] = copy.deepcopy(mod)
        return artifacts

    [...]

    if __name__ == "__main__":
        # Edit this section to customize the behavior of artifacts
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--url",
            type=str,
            default="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
        )
        args = parser.parse_args()
        artifacts = run_all_sessions(
            url=args.url,
        )
        print(artifacts)

As shown, we now have ``url`` factored out as an easily tunable parameter for the pipeline,
which allows us to run it with various data sources beyond those we started with (hence increasing the
pipeline's utility).

.. note::

    We get parametrization reflected in the framework-specific DAG file as well
    (compare with the :ref:`un-parametrized counterpart in the Basics section <iris_pipeline_dag>`):

    .. code-block:: python
        :emphasize-lines: 13, 28, 45

        # ./output/pipeline_parametrization/iris_pipeline_parametrized_dag.py

        import pathlib
        import pickle

        import iris_pipeline_parametrized_module
        from airflow import DAG
        from airflow.operators.python_operator import PythonOperator
        from airflow.utils.dates import days_ago

        [...]

        def task_iris_preprocessed(url):

            url = str(url)

            df = iris_pipeline_parametrized_module.get_iris_preprocessed(url)

            pickle.dump(df, open("/tmp/iris_pipeline_parametrized/variable_df.pickle", "wb"))

        [...]

        default_dag_args = {
            "owner": "airflow",
            "retries": 2,
            "start_date": days_ago(1),
            "params": {
                "url": "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
            },
        }

        with DAG(
            dag_id="iris_pipeline_parametrized_dag",
            schedule_interval="*/15 * * * *",
            max_active_runs=1,
            catchup=False,
            default_args=default_dag_args,
        ) as dag:

            [...]

            iris_preprocessed = PythonOperator(
                task_id="iris_preprocessed_task",
                python_callable=task_iris_preprocessed,
                op_kwargs={"url": "{{ params.url }}"},
            )

            [...]

    Hence, we can easily modify pipeline runs in the target system (Airflow in this case).

.. warning::

    Currently, ``input_parameters`` only accepts variables from literal assignment
    such as ``a = "123"``. For each variable to be parametrized, there should be only one
    literal assignment across all artifact code for the pipeline. For instance, if both
    ``a = "123"`` and ``a = "abc"`` exist in the pipeline's artifact code, we cannot make
    ``a`` an input parameter since its reference is ambiguous, i.e., we are not sure which
    literal assignment ``a`` refers to.

.. note::

   If you want hands-on practice,
   check out `this <https://github.com/LineaLabs/lineapy/blob/main/examples/tutorials/03_parametrize_pipelines.ipynb>`_ tutorial notebook.
